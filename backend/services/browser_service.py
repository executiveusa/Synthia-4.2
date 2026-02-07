"""
Synthia Browser Service - The Pauli Effect

Browser automation using Chrome DevTools Protocol (CDP) via Playwright.
Enables Synthia to browse websites, extract data, take screenshots, and interact with web pages.
"""

import os
import asyncio
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import base64
import json

# Playwright for browser automation
from playwright.async_api import async_playwright, Page, Browser, BrowserContext


@dataclass
class BrowserSession:
    """Represents an active browser session."""
    session_id: str
    page: Page
    context: BrowserContext
    browser: Browser
    url: Optional[str] = None
    

@dataclass
class ScrapedData:
    """Data extracted from a webpage."""
    url: str
    title: str
    content: str
    links: List[Dict[str, str]]
    images: List[Dict[str, str]]
    metadata: Dict[str, Any]
    screenshot: Optional[str] = None  # base64


class BrowserAction(str, Enum):
    """Available browser actions."""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCREENSHOT = "screenshot"
    EXTRACT = "extract"
    SCROLL = "scroll"
    EVALUATE = "evaluate"
    DOWNLOAD = "download"


class BrowserService:
    """
    Synthia's Browser Service for The Pauli Effect.
    
    Provides browser automation capabilities:
    - Navigate to URLs
    - Extract text and data
    - Take screenshots
    - Fill forms and click elements
    - Execute JavaScript
    - Download files
    """
    
    def __init__(self):
        self.sessions: Dict[str, BrowserSession] = {}
        self.playwright = None
        self._playwright_context = None
        
    async def _get_playwright(self):
        """Initialize playwright if not already done."""
        if self._playwright_context is None:
            self._playwright_context = await async_playwright().start()
        return self._playwright_context
    
    async def create_session(self, session_id: Optional[str] = None, headless: bool = True) -> str:
        """
        Create a new browser session.
        
        Args:
            session_id: Optional custom session ID
            headless: Whether to run browser in headless mode
            
        Returns:
            Session ID string
        """
        import uuid
        
        session_id = session_id or str(uuid.uuid4())
        pw = await self._get_playwright()
        
        # Launch browser
        browser = await pw.chromium.launch(headless=headless)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        # Store session
        self.sessions[session_id] = BrowserSession(
            session_id=session_id,
            page=page,
            context=context,
            browser=browser
        )
        
        return session_id
    
    async def navigate(self, session_id: str, url: str, wait_until: str = "networkidle") -> Dict[str, Any]:
        """
        Navigate to a URL.
        
        Args:
            session_id: Browser session ID
            url: URL to navigate to
            wait_until: When to consider navigation complete
            
        Returns:
            Navigation result with page info
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        try:
            response = await session.page.goto(url, wait_until=wait_until)
            session.url = url
            
            return {
                "success": True,
                "url": url,
                "title": await session.page.title(),
                "status": response.status if response else None,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
            }
    
    async def extract_data(self, session_id: str) -> ScrapedData:
        """
        Extract data from the current page.
        
        Args:
            session_id: Browser session ID
            
        Returns:
            ScrapedData object with page content
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        page = session.page
        
        # Get basic info
        title = await page.title()
        url = page.url
        
        # Extract main content (text)
        content = await page.evaluate("""() => {
            // Get main content, fallback to body
            const article = document.querySelector('article');
            const main = document.querySelector('main');
            const body = document.body;
            
            const element = article || main || body;
            return element.innerText.substring(0, 10000); // Limit to 10k chars
        }""")
        
        # Extract links
        links = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('a[href]')).map(a => ({
                text: a.innerText.trim().substring(0, 100),
                href: a.href,
            })).filter(l => l.text && l.href);
        }""")
        
        # Extract images
        images = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('img[src]')).map(img => ({
                alt: img.alt,
                src: img.src,
                width: img.width,
                height: img.height,
            })).filter(i => i.src);
        }""")
        
        # Extract metadata
        metadata = await page.evaluate("""() => {
            const meta = {};
            document.querySelectorAll('meta').forEach(m => {
                const name = m.getAttribute('name') || m.getAttribute('property');
                const content = m.getAttribute('content');
                if (name && content) {
                    meta[name] = content;
                }
            });
            return meta;
        }""")
        
        return ScrapedData(
            url=url,
            title=title,
            content=content,
            links=links[:50],  # Limit to 50 links
            images=images[:20],  # Limit to 20 images
            metadata=metadata
        )
    
    async def take_screenshot(self, session_id: str, full_page: bool = False) -> str:
        """
        Take a screenshot of the current page.
        
        Args:
            session_id: Browser session ID
            full_page: Whether to capture full page or viewport
            
        Returns:
            Base64 encoded screenshot
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        screenshot_bytes = await session.page.screenshot(full_page=full_page)
        return base64.b64encode(screenshot_bytes).decode('utf-8')
    
    async def click(self, session_id: str, selector: str) -> bool:
        """
        Click an element on the page.
        
        Args:
            session_id: Browser session ID
            selector: CSS selector for the element
            
        Returns:
            True if successful
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        try:
            await session.page.click(selector)
            return True
        except Exception as e:
            print(f"Click failed: {e}")
            return False
    
    async def type_text(self, session_id: str, selector: str, text: str) -> bool:
        """
        Type text into an input field.
        
        Args:
            session_id: Browser session ID
            selector: CSS selector for the input
            text: Text to type
            
        Returns:
            True if successful
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        try:
            await session.page.fill(selector, text)
            return True
        except Exception as e:
            print(f"Type failed: {e}")
            return False
    
    async def evaluate_javascript(self, session_id: str, script: str) -> Any:
        """
        Execute JavaScript on the page.
        
        Args:
            session_id: Browser session ID
            script: JavaScript code to execute
            
        Returns:
            Result of the JavaScript execution
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        return await session.page.evaluate(script)
    
    async def scroll(self, session_id: str, direction: str = "down", amount: int = 500) -> bool:
        """
        Scroll the page.
        
        Args:
            session_id: Browser session ID
            direction: "up" or "down"
            amount: Pixels to scroll
            
        Returns:
            True if successful
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        scroll_amount = amount if direction == "down" else -amount
        
        try:
            await session.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            return True
        except Exception as e:
            print(f"Scroll failed: {e}")
            return False
    
    async def close_session(self, session_id: str):
        """
        Close a browser session.
        
        Args:
            session_id: Browser session ID
        """
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        
        try:
            await session.context.close()
            await session.browser.close()
        except Exception as e:
            print(f"Error closing session: {e}")
        
        del self.sessions[session_id]
    
    async def close_all(self):
        """Close all browser sessions."""
        for session_id in list(self.sessions.keys()):
            await self.close_session(session_id)
        
        if self._playwright_context:
            await self._playwright_context.stop()
            self._playwright_context = None


# Singleton instance
_browser_service: Optional[BrowserService] = None


def get_browser_service() -> BrowserService:
    """Get or create browser service singleton."""
    global _browser_service
    if _browser_service is None:
        _browser_service = BrowserService()
    return _browser_service
