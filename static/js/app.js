/**
 * Multi-RAG Frontend Application
 * Chai Prep Brownish Theme with Live SSE Streaming & LangGraph Integration
 */

(function () {
    'use strict';

    // =========================================================================
    // SVG Icons
    // =========================================================================
    const ICONS = {
        // Streamlit Red Human Avatar Icon
        userAvatar: `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
            </svg>
        `,
        // Streamlit Orange Robot Avatar Icon
        aiAvatar: `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2M7.5 13A2.5 2.5 0 0 0 5 15.5 2.5 2.5 0 0 0 7.5 18a2.5 2.5 0 0 0 2.5-2.5A2.5 2.5 0 0 0 7.5 13m9 0a2.5 2.5 0 0 0-2.5 2.5 2.5 2.5 0 0 0 2.5 2.5 2.5 2.5 0 0 0 2.5-2.5 2.5 2.5 0 0 0-2.5-2.5"/>
            </svg>
        `,
        chevronRight: `
            <svg class="thinking-chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
        `,
        copy: `
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
        `,
        check: `
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
        `,
        trash: `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 6h18m-2 0v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6m3 0V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
            </svg>
        `,
        messageSquare: `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
        `,
        search: `
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
        `
    };

    // =========================================================================
    // State Store
    // =========================================================================
    const STORAGE_KEY_THEME = 'multi_rag_theme';
    const STORAGE_KEY_MODEL = 'multi_rag_model';
    const DEFAULT_MODEL = 'openai/gpt-oss-120b';

    let threads = [];
    let activeThreadId = null;
    let activeAbortController = null;
    let selectedFiles = [];

    // =========================================================================
    // DOM Elements
    // =========================================================================
    const DOM = {
        app: document.getElementById('app'),
        sidebar: document.getElementById('sidebar'),
        mobileMenuBtn: document.getElementById('mobileMenuBtn'),
        mobileCloseBtn: document.getElementById('mobileCloseBtn'),
        newChatBtn: document.getElementById('newChatBtn'),
        threadList: document.getElementById('threadList'),
        threadsCount: document.getElementById('threadsCount'),
        activeThreadBadge: document.getElementById('activeThreadBadge'),
        activeThreadShortId: document.getElementById('activeThreadShortId'),
        chatTitle: document.getElementById('chatTitle'),
        modelSelector: document.getElementById('modelSelector'),
        clearChatBtn: document.getElementById('clearChatBtn'),
        chatScrollContainer: document.getElementById('chatScrollContainer'),
        emptyState: document.getElementById('emptyState'),
        messagesContainer: document.getElementById('messagesContainer'),
        chatInput: document.getElementById('chatInput'),
        sendBtn: document.getElementById('sendBtn'),
        pipelineStatusBanner: document.getElementById('pipelineStatusBanner'),
        pipelineStatusText: document.getElementById('pipelineStatusText'),
        stopStreamBtn: document.getElementById('stopStreamBtn'),
        themeToggleBtn: document.getElementById('themeToggleBtn'),
        themeText: document.getElementById('themeText'),
        openIngestModalBtn: document.getElementById('openIngestModalBtn'),
        topIngestBtn: document.getElementById('topIngestBtn'),
        ingestModalBackdrop: document.getElementById('ingestModalBackdrop'),
        closeIngestModalBtn: document.getElementById('closeIngestModalBtn'),
        cancelIngestBtn: document.getElementById('cancelIngestBtn'),
        dropzone: document.getElementById('dropzone'),
        fileInput: document.getElementById('fileInput'),
        browseFilesBtn: document.getElementById('browseFilesBtn'),
        selectedFilesList: document.getElementById('selectedFilesList'),
        filesItems: document.getElementById('filesItems'),
        clearFilesBtn: document.getElementById('clearFilesBtn'),
        startIngestBtn: document.getElementById('startIngestBtn'),
        ingestProgress: document.getElementById('ingestProgress'),
        ingestProgressStatus: document.getElementById('ingestProgressStatus'),
        ingestProgressPercent: document.getElementById('ingestProgressPercent'),
        ingestAlert: document.getElementById('ingestAlert'),
        alertIcon: document.getElementById('alertIcon'),
        alertMessage: document.getElementById('alertMessage'),
    };

    // =========================================================================
    // Markdown Configuration
    // =========================================================================
    function setupMarked() {
        if (window.marked) {
            marked.setOptions({
                gfm: true,
                breaks: true,
                highlight: function (code, lang) {
                    if (window.hljs) {
                        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
                        return hljs.highlight(code, { language }).value;
                    }
                    return code;
                }
            });
        }
    }

    // =========================================================================
    // Theme Controller (Chai Prep Dark & Day)
    // =========================================================================
    function initTheme() {
        const saved = localStorage.getItem(STORAGE_KEY_THEME) || 'dark';
        applyTheme(saved);

        DOM.themeToggleBtn.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme') || 'dark';
            const next = current === 'dark' ? 'light' : 'dark';
            applyTheme(next);
            localStorage.setItem(STORAGE_KEY_THEME, next);
        });
    }

    function initModelSelector() {
        const savedModel = localStorage.getItem(STORAGE_KEY_MODEL);
        const modelIsAvailable = Array.from(DOM.modelSelector.options)
            .some(option => option.value === savedModel);
        DOM.modelSelector.value = modelIsAvailable ? savedModel : DEFAULT_MODEL;

        DOM.modelSelector.addEventListener('change', () => {
            localStorage.setItem(STORAGE_KEY_MODEL, DOM.modelSelector.value);
        });
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        document.body.className = theme === 'dark' ? 'theme-dark' : 'theme-light';

        const darkIcon = DOM.themeToggleBtn.querySelector('.theme-icon-dark');
        const lightIcon = DOM.themeToggleBtn.querySelector('.theme-icon-light');

        if (theme === 'dark') {
            darkIcon.style.display = 'inline-flex';
            lightIcon.style.display = 'none';
            DOM.themeText.textContent = 'Day Mode';
        } else {
            darkIcon.style.display = 'none';
            lightIcon.style.display = 'inline-flex';
            DOM.themeText.textContent = 'Dark Mode';
        }
    }

    // =========================================================================
    // Thread Manager (UUIDs, localStorage, Switching, Deleting)
    // =========================================================================
    async function fetchServerThreads() {
        try {
            const res = await fetch('/api/v1/conversations');
            if (!res.ok) throw new Error(`Server returned ${res.status}`);

            const data = await res.json();
            const previousActiveId = activeThreadId;
            threads = (data.threads || []).map(thread => ({
                id: thread.thread_id,
                title: thread.title || 'Conversation',
                createdAt: thread.created_at ? new Date(thread.created_at).getTime() : Date.now(),
                messages: [],
            }));

            if (threads.length === 0) {
                activeThreadId = null;
                createNewThread();
                return;
            }

            const activeThread = threads.find(thread => thread.id === previousActiveId) || threads[0];
            selectThread(activeThread.id);
        } catch (err) {
            console.debug('Failed to sync backend threads:', err);
        }
    }

    async function fetchThreadMessages(threadId) {
        try {
            const res = await fetch(`/api/v1/conversations/${threadId}`);
            if (res.ok) {
                const data = await res.json();
                if (data && Array.isArray(data.messages) && data.messages.length > 0) {
                    const current = threads.find(t => t.id === threadId);
                    if (current && (!current.messages || current.messages.length === 0)) {
                        current.messages = data.messages.map(m => {
                            const messageData = m.data || m;
                            const isUser = m.type === 'human' || m.type === 'user';
                            const additional = messageData.additional_kwargs || {};
                            const toolCalls = messageData.tool_calls || [];
                            const functionCall = additional.function_call;
                            const reasoning = messageData.reasoning
                                || additional.reasoning
                                || additional.reasoning_content
                                || additional.thinking
                                || '';
                            const tools = toolCalls.map(tool => ({
                                name: tool.name || 'tool',
                                label: tool.name || 'Tool call',
                                completed: true,
                            }));
                            if (functionCall) {
                                tools.push({
                                    name: functionCall.name || 'function',
                                    label: functionCall.name || 'Function call',
                                    completed: true,
                                });
                            }
                            return {
                                id: (isUser ? 'user-' : 'ai-') + Date.now() + Math.random().toString(36).substring(7),
                                role: isUser ? 'user' : 'assistant',
                                content: typeof messageData.content === 'string'
                                    ? messageData.content
                                    : JSON.stringify(messageData.content ?? ''),
                                reasoning,
                                tools,
                            };
                        });
                        saveThreads();
                        if (activeThreadId === threadId) {
                            renderMessages(current.messages);
                        }
                    }
                }
            }
        } catch (err) {
            console.debug('Failed to load thread messages:', err);
        }
    }

    function initThreads() {
        threads = [];
        activeThreadId = null;
        renderThreadList();
        fetchServerThreads();

        DOM.newChatBtn.addEventListener('click', () => createNewThread());
        DOM.clearChatBtn.addEventListener('click', clearCurrentChat);
    }

    function saveThreads() {
        renderThreadList();
    }

    function generateUUID() {
        if (typeof crypto !== 'undefined' && crypto.randomUUID) {
            return crypto.randomUUID();
        }
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            const r = (Math.random() * 16) | 0;
            const v = c === 'x' ? r : (r & 0x3) | 0x8;
            return v.toString(16);
        });
    }

    function createNewThread() {
        const id = generateUUID();
        const newThread = {
            id: id,
            title: 'New Conversation',
            createdAt: Date.now(),
            messages: []
        };
        threads.unshift(newThread);
        saveThreads();
        selectThread(id);

        // Close mobile sidebar if open
        if (window.innerWidth <= 768) {
            DOM.sidebar.classList.remove('open');
        }
    }

    function selectThread(id) {
        activeThreadId = id;

        const current = getActiveThread();
        if (current) {
            DOM.chatTitle.textContent = current.title || 'Conversation';
            DOM.activeThreadShortId.textContent = id.slice(0, 8) + '...';
            DOM.activeThreadBadge.title = `Full Thread ID: ${id}`;
            renderMessages(current.messages || []);
            if (!current.messages || current.messages.length === 0) {
                fetchThreadMessages(id);
            }
        }

        renderThreadList();
    }

    function getActiveThread() {
        return threads.find(t => t.id === activeThreadId);
    }

    function deleteThread(id, event) {
        if (event) event.stopPropagation();
        threads = threads.filter(t => t.id !== id);

        // Notify backend to delete from SQLite checkpointer and clean up thread data
        fetch(`/api/v1/conversations/${id}`, { method: 'DELETE' }).catch(err => {
            console.debug('Failed to delete thread on server:', err);
        });

        if (activeThreadId === id) {
            if (threads.length > 0) {
                selectThread(threads[0].id);
            } else {
                createNewThread();
            }
        } else {
            saveThreads();
        }
    }

    function clearCurrentChat() {
        if (activeThreadId) deleteThread(activeThreadId);
    }

    function renderThreadList() {
        DOM.threadList.innerHTML = '';
        DOM.threadsCount.textContent = threads.length;

        threads.forEach(thread => {
            const item = document.createElement('div');
            item.className = `thread-item ${thread.id === activeThreadId ? 'active' : ''}`;
            item.onclick = () => selectThread(thread.id);

            const content = document.createElement('div');
            content.className = 'thread-item-content';

            const icon = document.createElement('span');
            icon.className = 'thread-item-icon';
            icon.innerHTML = ICONS.messageSquare;

            const title = document.createElement('span');
            title.className = 'thread-item-title';
            title.textContent = thread.title || 'Untitled Thread';

            content.appendChild(icon);
            content.appendChild(title);

            const delBtn = document.createElement('button');
            delBtn.className = 'thread-item-delete';
            delBtn.title = 'Delete thread';
            delBtn.innerHTML = ICONS.trash;
            delBtn.onclick = (e) => deleteThread(thread.id, e);

            item.appendChild(content);
            item.appendChild(delBtn);

            DOM.threadList.appendChild(item);
        });
    }

    // =========================================================================
    // Chat Timeline & Message Rendering
    // =========================================================================
    function renderMessages(messages) {
        DOM.messagesContainer.innerHTML = '';

        if (!messages || messages.length === 0) {
            DOM.emptyState.style.display = 'flex';
            DOM.messagesContainer.style.display = 'none';
            return;
        }

        DOM.emptyState.style.display = 'none';
        DOM.messagesContainer.style.display = 'flex';

        messages.forEach(msg => {
            appendMessageToDOM(msg, false);
        });

        scrollToBottom();
    }

    function appendMessageToDOM(msg, shouldScroll = true) {
        const row = document.createElement('div');
        row.className = `message-row ${msg.role}`;
        row.id = msg.id || ('msg-' + Date.now());

        // Avatar
        const avatar = document.createElement('div');
        avatar.className = `message-avatar ${msg.role === 'user' ? 'user-avatar' : 'ai-avatar'}`;
        avatar.innerHTML = msg.role === 'user' ? ICONS.userAvatar : ICONS.aiAvatar;
        row.appendChild(avatar);

        // Content Wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'message-content-wrapper';

        // Sender Label
        const sender = document.createElement('div');
        sender.className = 'message-sender';
        sender.textContent = msg.role === 'user' ? 'You' : 'Chai Prep AI';
        wrapper.appendChild(sender);

        // Tool execution badges (if any)
        if (msg.tools && msg.tools.length > 0) {
            const toolContainer = document.createElement('div');
            toolContainer.className = 'tools-list-container';
            msg.tools.forEach(tool => {
                const badge = document.createElement('div');
                badge.className = `tool-execution-badge ${tool.completed ? 'completed' : ''}`;
                badge.innerHTML = `${ICONS.search} <span>${escapeHtml(tool.label || 'Tool: ' + tool.name)}</span>`;
                toolContainer.appendChild(badge);
            });
            wrapper.appendChild(toolContainer);
        }

        // Reasoning / Thinking Accordion (if present)
        if (msg.reasoning) {
            const accordion = createThinkingAccordion(msg.reasoning, false);
            wrapper.appendChild(accordion);
        }

        // Message Body
        const body = document.createElement('div');
        body.className = 'message-body';

        if (msg.role === 'user') {
            body.textContent = msg.content;
        } else {
            body.innerHTML = renderMarkdown(msg.content);
            enhanceCodeBlocks(body);
        }

        wrapper.appendChild(body);
        row.appendChild(wrapper);

        DOM.messagesContainer.appendChild(row);

        if (shouldScroll) {
            scrollToBottom();
        }

        return row;
    }

    function createTechstackAccordion() {
        const details = document.createElement('details');
        details.className = 'techstack-flow-accordion';
        details.open = true;

        const summary = document.createElement('summary');
        summary.className = 'techstack-summary';
        summary.innerHTML = `
            <span class="pulsing-amber-dot"></span>
            <span class="techstack-label">
                <span>⚡ Pipeline Execution Trace</span>
                <span class="techstack-status-badge">Running</span>
            </span>
            <svg class="techstack-chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
        `;

        const content = document.createElement('div');
        content.className = 'techstack-content';

        const timeline = document.createElement('div');
        timeline.className = 'techstack-timeline';
        content.appendChild(timeline);

        details.appendChild(summary);
        details.appendChild(content);

        return {
            element: details,
            timeline: timeline,
            summary: summary,
            statusBadge: summary.querySelector('.techstack-status-badge'),
            addOrUpdateStep: function(nodeId, title, desc, status = 'running') {
                let step = timeline.querySelector(`[data-node="${nodeId}"]`);
                if (!step) {
                    step = document.createElement('div');
                    step.className = `techstack-step ${status}`;
                    step.setAttribute('data-node', nodeId);
                    step.innerHTML = `
                        <div class="techstack-step-marker"></div>
                        <div class="techstack-step-info">
                            <div class="techstack-step-title">${escapeHtml(title)}</div>
                            <div class="techstack-step-desc">${escapeHtml(desc)}</div>
                        </div>
                    `;
                    timeline.appendChild(step);
                } else {
                    step.className = `techstack-step ${status}`;
                    const titleEl = step.querySelector('.techstack-step-title');
                    const descEl = step.querySelector('.techstack-step-desc');
                    if (titleEl) titleEl.textContent = title;
                    if (descEl) descEl.textContent = desc;
                }

                if (status === 'running') {
                    this.statusBadge.textContent = 'Running';
                    this.statusBadge.className = 'techstack-status-badge';
                } else if (status === 'blocked') {
                    this.statusBadge.textContent = 'Blocked';
                    this.statusBadge.className = 'techstack-status-badge blocked';
                }
            },
            complete: function(isBlocked = false) {
                if (isBlocked) {
                    this.statusBadge.textContent = 'Blocked';
                    this.statusBadge.className = 'techstack-status-badge blocked';
                } else {
                    this.statusBadge.textContent = 'Completed';
                    this.statusBadge.className = 'techstack-status-badge completed';
                }
                // Auto toggle off after response arrives so user can manually view
                details.open = false;
            }
        };
    }

    function createThinkingAccordion(reasoningText, isOpen = true) {
        const details = document.createElement('details');
        details.className = 'thinking-accordion';
        if (isOpen) details.open = true;

        const summary = document.createElement('summary');
        summary.className = 'thinking-summary';
        summary.innerHTML = `
            <span class="pulsing-amber-dot"></span>
            <span class="thinking-label">
                <span>Reasoning & Thought Process</span>
                <span class="thinking-timer">Deliberation</span>
            </span>
            ${ICONS.chevronRight}
        `;

        const content = document.createElement('div');
        content.className = 'thinking-content';
        content.textContent = reasoningText;

        details.appendChild(summary);
        details.appendChild(content);

        return details;
    }

    function renderMarkdown(rawText) {
        if (!rawText) return '';
        if (window.marked) {
            try {
                return marked.parse(rawText);
            } catch (e) {
                console.error('Marked error:', e);
                return escapeHtml(rawText);
            }
        }
        return escapeHtml(rawText);
    }

    function enhanceCodeBlocks(container) {
        const pres = container.querySelectorAll('pre');
        pres.forEach(pre => {
            if (pre.parentElement && pre.parentElement.classList.contains('code-block-wrapper')) {
                return;
            }

            const code = pre.querySelector('code');
            let lang = 'code';
            if (code) {
                const classes = code.className.split(' ');
                for (const cls of classes) {
                    if (cls.startsWith('language-')) {
                        lang = cls.replace('language-', '');
                        break;
                    }
                }
            }

            const wrapper = document.createElement('div');
            wrapper.className = 'code-block-wrapper';

            const header = document.createElement('div');
            header.className = 'code-header';

            const langLabel = document.createElement('span');
            langLabel.textContent = lang;

            const copyBtn = document.createElement('button');
            copyBtn.className = 'code-copy-btn';
            copyBtn.innerHTML = `${ICONS.copy} <span>Copy</span>`;
            copyBtn.onclick = () => {
                const textToCopy = code ? code.innerText : pre.innerText;
                navigator.clipboard.writeText(textToCopy).then(() => {
                    copyBtn.innerHTML = `${ICONS.check} <span>Copied!</span>`;
                    setTimeout(() => {
                        copyBtn.innerHTML = `${ICONS.copy} <span>Copy</span>`;
                    }, 2000);
                });
            };

            header.appendChild(langLabel);
            header.appendChild(copyBtn);

            pre.parentNode.insertBefore(wrapper, pre);
            wrapper.appendChild(header);
            wrapper.appendChild(pre);

            if (window.hljs && code) {
                hljs.highlightElement(code);
            }
        });
    }

    function scrollToBottom() {
        requestAnimationFrame(() => {
            DOM.chatScrollContainer.scrollTop = DOM.chatScrollContainer.scrollHeight;
        });
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // =========================================================================
    // Chat Workflow & Live Pipeline Streaming (SSE)
    // =========================================================================
    async function sendMessage(text) {
        const query = (text || DOM.chatInput.value || '').trim();
        if (!query) return;

        const currentThread = getActiveThread();
        if (!currentThread) return;

        // Auto update thread title on first message
        if (currentThread.messages.length === 0) {
            currentThread.title = query.length > 32 ? query.slice(0, 32) + '...' : query;
            DOM.chatTitle.textContent = currentThread.title;
        }

        // Add user message
        const userMsg = {
            id: 'user-' + Date.now(),
            role: 'user',
            content: query
        };
        currentThread.messages.push(userMsg);

        // Hide empty state and append user bubble
        DOM.emptyState.style.display = 'none';
        DOM.messagesContainer.style.display = 'flex';
        appendMessageToDOM(userMsg, true);

        // Clear input and reset height
        DOM.chatInput.value = '';
        DOM.chatInput.style.height = 'auto';
        saveThreads();

        // Create Assistant Placeholder in DOM
        const assistantMsgId = 'ai-' + Date.now();
        const assistantRow = document.createElement('div');
        assistantRow.className = 'message-row assistant';
        assistantRow.id = assistantMsgId;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar ai-avatar';
        avatar.innerHTML = ICONS.aiAvatar;
        assistantRow.appendChild(avatar);

        const contentWrapper = document.createElement('div');
        contentWrapper.className = 'message-content-wrapper';

        const sender = document.createElement('div');
        sender.className = 'message-sender';
        sender.textContent = 'Chai Prep AI';
        contentWrapper.appendChild(sender);

        // Live Tool Badges Container
        const toolsContainer = document.createElement('div');
        toolsContainer.className = 'tools-list-container';
        contentWrapper.appendChild(toolsContainer);

        // Techstack Flow & Guardrail Timeline Block (live visual only)
        let techstackBlock = null;

        // Reasoning Block (hidden initially)
        let reasoningBlock = null;
        let reasoningAccumulator = '';


        // Live Message Body
        const messageBody = document.createElement('div');
        messageBody.className = 'message-body';
        messageBody.innerHTML = '<span class="streaming-cursor"></span>';
        contentWrapper.appendChild(messageBody);

        assistantRow.appendChild(contentWrapper);
        DOM.messagesContainer.appendChild(assistantRow);
        scrollToBottom();

        // Set UI to Streaming Mode
        setStreamingMode(true, 'RAG Pipeline Active...');

        let tokenAccumulator = '';
        let toolsList = [];

        activeAbortController = new AbortController();

        try {
            // Initiate SSE streaming request
            const response = await fetch('/api/v1/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-thread-id': activeThreadId,
                    'thread_id': activeThreadId,
                    'x-user-id': 'guest-user',
                    'user_id': 'guest-user'
                },
                body: JSON.stringify({
                    message: query,
                    stream: true,
                    metadata: {
                        thread_id: activeThreadId,
                        user_id: 'guest-user',
                        model: DOM.modelSelector.value || DEFAULT_MODEL
                    }
                }),
                signal: activeAbortController.signal
            });

            if (!response.ok) {
                let errDetail = `Server returned ${response.status} ${response.statusText}`;
                try {
                    const errJson = await response.json();
                    if (errJson && errJson.detail) {
                        errDetail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
                    }
                } catch (_) {}
                throw new Error(errDetail);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop(); // keep remainder

                for (let line of lines) {
                    line = line.trim();
                    if (!line || !line.startsWith('data:')) continue;

                    const rawData = line.slice(5).trim();
                    if (!rawData || rawData === '[DONE]') continue;

                    try {
                        const event = JSON.parse(rawData);

                        // 0. Techstack Pipeline & Guardrail Node Flow Event
                        if (event.type === 'node_flow') {
                            if (!techstackBlock) {
                                techstackBlock = createTechstackAccordion();
                                contentWrapper.insertBefore(techstackBlock.element, messageBody);
                            }
                            const nodeId = event.node || 'step';
                            const title = event.title || 'Pipeline Node';
                            const desc = event.description || '';
                            const status = event.status || 'running';
                            techstackBlock.addOrUpdateStep(nodeId, title, desc, status);
                            setStreamingMode(true, `${title}...`);
                            scrollToBottom();
                        }

                        // 1. Reasoning Event
                        if (event.reasoning || event.type === 'reasoning') {
                            const rText = event.reasoning || event.content || '';
                            reasoningAccumulator += rText;
                            if (!reasoningBlock) {
                                reasoningBlock = createThinkingAccordion(reasoningAccumulator, true);
                                contentWrapper.insertBefore(reasoningBlock, messageBody);
                            } else {
                                const cDiv = reasoningBlock.querySelector('.thinking-content');
                                if (cDiv) cDiv.textContent = reasoningAccumulator;
                            }
                            setStreamingMode(true, 'Thinking & Deliberating...');
                        }

                        // 2. Tool Start Event
                        if (event.event === 'tool_start' || event.tool_start || event.type === 'tool_start') {
                            const toolName = event.tool || event.name || 'retriever';
                            const toolInput = event.tool_input || event.input || '';
                            const toolInfo = {
                                name: toolName,
                                label: `🔍 Searching knowledge base with ${toolName}...`,
                                completed: false
                            };
                            toolsList.push(toolInfo);

                            const badge = document.createElement('div');
                            badge.className = 'tool-execution-badge';
                            badge.id = `tool-badge-${toolsList.length}`;
                            badge.innerHTML = `${ICONS.search} <span>${escapeHtml(toolInfo.label)}</span>`;
                            toolsContainer.appendChild(badge);
                            setStreamingMode(true, `Executing ${toolName}...`);
                            scrollToBottom();
                        }

                        // 3. Tool End Event
                        if (event.event === 'tool_end' || event.tool_end || event.type === 'tool_end') {
                            const lastBadge = toolsContainer.querySelector('.tool-execution-badge:not(.completed)');
                            if (lastBadge) {
                                lastBadge.classList.add('completed');
                            }
                            setStreamingMode(true, 'Synthesizing retrieval results...');
                        }

                        // 4. Token Event
                        if (event.token !== undefined || event.type === 'token') {
                            const t = event.token !== undefined ? event.token : (event.content || '');
                            tokenAccumulator += t;
                            messageBody.innerHTML = renderMarkdown(tokenAccumulator) + '<span class="streaming-cursor"></span>';
                            enhanceCodeBlocks(messageBody);
                            scrollToBottom();
                        }

                        // 5. Final Event
                        if (event.final !== undefined || event.event === 'final') {
                            const finalText = event.final || event.content || tokenAccumulator;
                            tokenAccumulator = finalText;
                            messageBody.innerHTML = renderMarkdown(tokenAccumulator);
                            enhanceCodeBlocks(messageBody);
                            scrollToBottom();
                        }

                        // 6. Error Event
                        if (event.error) {
                            messageBody.innerHTML = `<div class="ingest-alert error">${escapeHtml(event.error)}</div>`;
                        }

                    } catch (parseErr) {
                        console.warn('Could not parse SSE JSON line:', line, parseErr);
                    }
                }
            }

            // Auto toggle off techstack accordion once response arrives so user can view it manually
            if (techstackBlock) {
                const isBlocked = !!contentWrapper.querySelector('.techstack-step.blocked');
                techstackBlock.complete(isBlocked);
            }

            // Clean up cursor after stream completes
            messageBody.innerHTML = renderMarkdown(tokenAccumulator || '(No response received)');
            enhanceCodeBlocks(messageBody);

            // Persist assistant message to thread
            const savedAiMsg = {
                id: assistantMsgId,
                role: 'assistant',
                content: tokenAccumulator,
                reasoning: reasoningAccumulator || null,
                tools: toolsList
            };
            currentThread.messages.push(savedAiMsg);
            saveThreads();

        } catch (streamErr) {
            if (techstackBlock) {
                techstackBlock.complete(false);
            }
            if (streamErr.name === 'AbortError') {
                messageBody.innerHTML = renderMarkdown(tokenAccumulator + '\n\n*(Generation stopped by user)*');
            } else {
                console.error('Chat stream error:', streamErr);
                messageBody.innerHTML = `<div class="ingest-alert error"><strong>Error:</strong> ${escapeHtml(streamErr.message || 'Stream connection failed.')}</div>`;
            }
        } finally {
            setStreamingMode(false);
            activeAbortController = null;
            scrollToBottom();
        }
    }

    function setStreamingMode(isStreaming, statusText = '') {
        DOM.sendBtn.disabled = isStreaming;
        DOM.pipelineStatusBanner.style.display = isStreaming ? 'flex' : 'none';
        if (statusText) {
            DOM.pipelineStatusText.textContent = statusText;
        }
    }

    function stopActiveStream() {
        if (activeAbortController) {
            activeAbortController.abort();
            setStreamingMode(false);
        }
    }

    // =========================================================================
    // Document Ingestion Modal & Upload Handler
    // =========================================================================
    function initIngestModal() {
        const openModal = () => {
            DOM.ingestModalBackdrop.style.display = 'flex';
            resetIngestModal();
        };

        const closeModal = () => {
            DOM.ingestModalBackdrop.style.display = 'none';
        };

        DOM.openIngestModalBtn.addEventListener('click', openModal);
        DOM.topIngestBtn.addEventListener('click', openModal);
        DOM.closeIngestModalBtn.addEventListener('click', closeModal);
        DOM.cancelIngestBtn.addEventListener('click', closeModal);

        DOM.ingestModalBackdrop.addEventListener('click', (e) => {
            if (e.target === DOM.ingestModalBackdrop) closeModal();
        });

        // Dropzone interactions
        DOM.browseFilesBtn.addEventListener('click', () => DOM.fileInput.click());
        DOM.dropzone.addEventListener('click', (e) => {
            if (e.target !== DOM.browseFilesBtn) DOM.fileInput.click();
        });

        DOM.fileInput.addEventListener('change', (e) => {
            handleFilesSelected(e.target.files);
        });

        DOM.dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            DOM.dropzone.classList.add('dragover');
        });

        DOM.dropzone.addEventListener('dragleave', () => {
            DOM.dropzone.classList.remove('dragover');
        });

        DOM.dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            DOM.dropzone.classList.remove('dragover');
            if (e.dataTransfer && e.dataTransfer.files) {
                handleFilesSelected(e.dataTransfer.files);
            }
        });

        DOM.clearFilesBtn.addEventListener('click', () => {
            selectedFiles = [];
            renderSelectedFiles();
        });

        DOM.startIngestBtn.addEventListener('click', startIngestion);
    }

    function resetIngestModal() {
        selectedFiles = [];
        renderSelectedFiles();
        DOM.ingestProgress.style.display = 'none';
        DOM.ingestAlert.style.display = 'none';
        DOM.startIngestBtn.disabled = true;
    }

    function handleFilesSelected(fileList) {
        if (!fileList || fileList.length === 0) return;
        const allowedExtensions = ['.pdf', '.docx', '.pptx', '.txt', '.html'];

        for (let i = 0; i < fileList.length; i++) {
            const file = fileList[i];
            const ext = '.' + file.name.split('.').pop().toLowerCase();
            if (allowedExtensions.includes(ext)) {
                if (!selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
                    selectedFiles.push(file);
                }
            } else {
                showIngestAlert('error', `Unsupported file: ${file.name}. Allowed: PDF, DOCX, PPTX, TXT, HTML.`);
            }
        }

        renderSelectedFiles();
    }

    function renderSelectedFiles() {
        DOM.filesItems.innerHTML = '';
        if (selectedFiles.length === 0) {
            DOM.selectedFilesList.style.display = 'none';
            DOM.startIngestBtn.disabled = true;
            return;
        }

        DOM.selectedFilesList.style.display = 'block';
        DOM.startIngestBtn.disabled = false;

        selectedFiles.forEach((file, index) => {
            const row = document.createElement('div');
            row.className = 'file-row';

            const name = document.createElement('span');
            name.className = 'file-row-name';
            name.textContent = file.name;

            const size = document.createElement('span');
            size.className = 'file-row-size';
            size.textContent = formatBytes(file.size);

            row.appendChild(name);
            row.appendChild(size);
            DOM.filesItems.appendChild(row);
        });
    }

    function formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    async function startIngestion() {
        if (selectedFiles.length === 0) return;

        const ingestionPassword = prompt('Enter authorized password for ingestion:');
        if (ingestionPassword === null) {
            return;
        }

        DOM.startIngestBtn.disabled = true;
        DOM.ingestProgress.style.display = 'flex';
        DOM.ingestAlert.style.display = 'none';
        DOM.ingestProgressStatus.textContent = 'Uploading documents to ingestion pipeline...';

        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('file', file);
        });

        try {
            const response = await fetch('/api/v1/ingest', {
                method: 'POST',
                headers: {
                    'x-ingestion-password': ingestionPassword,
                    'x-thread-id': activeThreadId,
                    'thread_id': activeThreadId,
                    'x-user-id': 'guest-user',
                    'user_id': 'guest-user'
                },
                body: formData
            });

            if (!response.ok) {
                let errText = `Ingestion failed (${response.status})`;
                try {
                    const errJson = await response.json();
                    if (errJson && errJson.detail) {
                        errText = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
                    }
                } catch (_) {}
                throw new Error(errText);
            }

            const data = await response.json();
            DOM.ingestProgress.style.display = 'none';
            showIngestAlert('success', `Successfully indexed ${selectedFiles.length} file(s) into the knowledge base!`);
            selectedFiles = [];
            renderSelectedFiles();

        } catch (e) {
            console.error('Ingestion error:', e);
            DOM.ingestProgress.style.display = 'none';
            DOM.startIngestBtn.disabled = false;
            showIngestAlert('error', `Error during document ingestion: ${e.message}`);
        }
    }

    function showIngestAlert(type, message) {
        DOM.ingestAlert.className = `ingest-alert ${type}`;
        DOM.ingestAlert.style.display = 'flex';
        DOM.alertMessage.textContent = message;
    }

    // =========================================================================
    // UI Event Listeners & Auto-Grow Input
    // =========================================================================
    function initUIEvents() {
        // Send button click
        DOM.sendBtn.addEventListener('click', () => sendMessage());

        // Stop stream click
        DOM.stopStreamBtn.addEventListener('click', stopActiveStream);

        // Input keyboard events
        DOM.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Auto-expand input height
        DOM.chatInput.addEventListener('input', () => {
            DOM.chatInput.style.height = 'auto';
            DOM.chatInput.style.height = Math.min(DOM.chatInput.scrollHeight, 180) + 'px';
        });

        // Quick prompts
        document.querySelectorAll('.quick-prompt-card').forEach(card => {
            card.addEventListener('click', () => {
                const prompt = card.getAttribute('data-prompt');
                if (prompt) {
                    DOM.chatInput.value = prompt;
                    sendMessage(prompt);
                }
            });
        });

        // Mobile sidebar toggle
        DOM.mobileMenuBtn.addEventListener('click', () => {
            DOM.sidebar.classList.toggle('open');
        });

        DOM.mobileCloseBtn.addEventListener('click', () => {
            DOM.sidebar.classList.remove('open');
        });
    }

    // =========================================================================
    // App Initialization
    // =========================================================================
    function init() {
        setupMarked();
        initTheme();
        initModelSelector();
        initThreads();
        initIngestModal();
        initUIEvents();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
