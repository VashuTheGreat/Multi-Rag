tailwind.config = {
    theme: {
        extend: {
            fontFamily: {
                sans: ['"Plus Jakarta Sans"', 'Outfit', 'sans-serif'],
            },
            keyframes: {
                'spin-orbit-x': {
                    '0%': { transform: 'rotateX(75deg) rotateY(15deg) rotateZ(0deg)' },
                    '100%': { transform: 'rotateX(75deg) rotateY(15deg) rotateZ(360deg)' },
                },
                'spin-orbit-y': {
                    '0%': { transform: 'rotateX(75deg) rotateY(-15deg) rotateZ(120deg)' },
                    '100%': { transform: 'rotateX(75deg) rotateY(-15deg) rotateZ(480deg)' },
                },
                'spin-orbit-z': {
                    '0%': { transform: 'rotateX(60deg) rotateY(45deg) rotateZ(240deg)' },
                    '100%': { transform: 'rotateX(60deg) rotateY(45deg) rotateZ(600deg)' },
                }
            },
            animation: {
                'orbit-x': 'spin-orbit-x 8s linear infinite',
                'orbit-y': 'spin-orbit-y 6s linear infinite',
                'orbit-z': 'spin-orbit-z 10s linear infinite',
            }
        }
    }
}
