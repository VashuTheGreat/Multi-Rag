


from transformers import AutoProcessor,AutoModelForImageTextToText
from PIL import Image
import sys
from exception import MyException

async def image_to_text(image_path:str)->str:
    try:
        image=Image.open(image_path).convert('RGB')

        processor = AutoProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
        model = AutoModelForImageTextToText.from_pretrained("Salesforce/blip-image-captioning-large")


        inputs = processor(images=image, return_tensors="pt")
        # Generate a caption
        generated_ids = model.generate(**inputs)
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
        return generated_text
    
    except Exception as e:
        MyException(f"Error in image_to_text: {str(e)}",sys)

