"""
═══════════════════════════════════════════════════════════════════════════════
🎯 SMART BARGAIN AI - Professional Negotiation System
Powered by Llama 3.1 8B | Real-time Market Simulation
═══════════════════════════════════════════════════════════════════════════════
"""

import json
import time
import threading
import random
import requests
import os
import sys
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 ENHANCED UI SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

class Colors:
    """ANSI color codes for terminal styling"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Text Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright Colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background Colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'

class UIManager:
    """Enhanced UI manager for professional display"""
    
    @staticmethod
    def clear_screen():
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_header(title: str, subtitle: str = ""):
        """Print professional header"""
        width = 80
        print(f"{Colors.BRIGHT_CYAN}{'═' * width}{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}║{Colors.BRIGHT_WHITE}{title.center(width-2)}{Colors.BRIGHT_CYAN}║{Colors.RESET}")
        if subtitle:
            print(f"{Colors.BRIGHT_CYAN}║{Colors.BRIGHT_YELLOW}{subtitle.center(width-2)}{Colors.BRIGHT_CYAN}║{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{'═' * width}{Colors.RESET}")
    
    @staticmethod
    def print_section(title: str, content: str = "", color: str = Colors.BRIGHT_BLUE):
        """Print section with styling"""
        print(f"\n{color}▓▓▓ {title} ▓▓▓{Colors.RESET}")
        if content:
            print(f"{Colors.WHITE}{content}{Colors.RESET}")
    
    @staticmethod
    def print_deal_status(status: str, price: int = 0, savings: int = 0):
        """Print deal status with visual flair"""
        if "SUCCESS" in status.upper():
            print(f"\n{Colors.BG_GREEN}{Colors.BLACK} 🎉 DEAL SUCCESSFUL! 🎉 {Colors.RESET}")
            print(f"{Colors.BRIGHT_GREEN}💰 Final Price: ₹{price:,}{Colors.RESET}")
            if savings > 0:
                print(f"{Colors.BRIGHT_GREEN}💵 You Saved: ₹{savings:,}{Colors.RESET}")
        elif "TIMEOUT" in status.upper():
            print(f"\n{Colors.BG_RED}{Colors.WHITE} ⏰ TIME'S UP! ⏰ {Colors.RESET}")
        elif "REJECTED" in status.upper():
            print(f"\n{Colors.BG_YELLOW}{Colors.BLACK} ❌ NEGOTIATION ENDED ❌ {Colors.RESET}")
    
    @staticmethod
    def print_timer(seconds_left: int):
        """Print countdown timer with colors"""
        if seconds_left > 60:
            color = Colors.BRIGHT_GREEN
            icon = "🟢"
        elif seconds_left > 30:
            color = Colors.BRIGHT_YELLOW
            icon = "🟡"
        else:
            color = Colors.BRIGHT_RED
            icon = "🔴"
        
        minutes = seconds_left // 60
        seconds = seconds_left % 60
        print(f"{color}{icon} Time: {minutes:02d}:{seconds:02d}{Colors.RESET}", end=" ")
    
    @staticmethod
    def animate_text(text: str, delay: float = 0.03):
        """Animate text character by character"""
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()

# ═══════════════════════════════════════════════════════════════════════════════
# 🧠 SMART AI INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

class SmartLlamaClient:
    """Enhanced Llama client with better error handling and responses"""
    
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.model = "llama3.1:8b"
        self.connected = False
        self.response_cache = {}
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize connection with visual feedback"""
        print(f"{Colors.BRIGHT_CYAN}🔌 Connecting to AI Brain (Llama 3.1)...{Colors.RESET}")
        
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=3)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model["name"] for model in models]
                
                if any("llama3.1" in name for name in model_names):
                    print(f"{Colors.BRIGHT_GREEN}✅ AI Connected! Using Llama 3.1 8B{Colors.RESET}")
                    self.connected = True
                else:
                    print(f"{Colors.BRIGHT_YELLOW}⚠️  Llama 3.1 not found. Run: ollama pull llama3.1:8b{Colors.RESET}")
                    self._fallback_mode()
            else:
                raise ConnectionError("Service not responding")
                
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}❌ AI Connection Failed{Colors.RESET}")
            self._fallback_mode()
    
    def _fallback_mode(self):
        """Enter fallback mode with user choice"""
        print(f"\n{Colors.BRIGHT_YELLOW}🤖 FALLBACK MODE AVAILABLE{Colors.RESET}")
        print(f"{Colors.WHITE}• Smart simulated AI responses{Colors.RESET}")
        print(f"{Colors.WHITE}• Full personality system active{Colors.RESET}")
        print(f"{Colors.WHITE}• All features working{Colors.RESET}")
        
        choice = input(f"\n{Colors.BRIGHT_CYAN}Continue with Smart AI? (y/n): {Colors.RESET}").lower()
        if choice != 'y':
            print(f"{Colors.BRIGHT_RED}Setup Ollama first, then restart!{Colors.RESET}")
            sys.exit(1)
        
        self.connected = False
        print(f"{Colors.BRIGHT_GREEN}🚀 Smart AI Activated!{Colors.RESET}\n")
    
    def generate_response(self, personality_prompt: str, context: str, max_tokens: int = 150) -> str:
        """Generate intelligent response"""
        if self.connected:
            return self._llama_response(personality_prompt + "\n\n" + context, max_tokens)
        else:
            return self._smart_fallback_response(personality_prompt, context)
    
    def _llama_response(self, prompt: str, max_tokens: int) -> str:
        """Get response from Llama 3.1"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.9,
                    "top_p": 0.95,
                    "max_tokens": max_tokens,
                    "stop": ["Human:", "User:", "\n\n\n"]
                }
            }
            
            response = requests.post(f"{self.host}/api/generate", json=payload, timeout=25)
            
            if response.status_code == 200:
                result = response.json().get("response", "").strip()
                return self._clean_response(result)
            
        except Exception:
            pass
        
        return self._smart_fallback_response("", "")
    
    def _smart_fallback_response(self, personality_prompt: str, context: str) -> str:
        """Generate smart fallback responses based on context"""
        
        # Personality-based responses
        if "aggressive" in personality_prompt.lower():
            responses = [
                "Premium quality demands premium price! Time is running out, my friend.",
                "These products won't last long at this price. Other buyers are calling!",
                "You know quality when you see it. Let's close this deal now!",
                "Market rates are rising daily. This is your best opportunity!"
            ]
        elif "diplomatic" in personality_prompt.lower():
            responses = [
                "I appreciate your business sense. Let's find a price that works for both of us.",
                "Quality speaks for itself here. I'm confident we can reach an agreement.",
                "Your offer shows you understand value. How about we meet in the middle?",
                "I respect your negotiation skills. Let's work together on this."
            ]
        elif "cunning" in personality_prompt.lower():
            responses = [
                "Ah, a smart buyer! I respect that. For someone like you, I might reconsider...",
                "You remind me of myself when I started. Perhaps we can make something work.",
                "I have other interested buyers, but I like your approach. Let me think...",
                "You drive a hard bargain! That's exactly what I'd do in your position."
            ]
        else:
            responses = [
                "Your offer is interesting. Let me counter with something fair.",
                "I can see you're serious about this deal. Here's what I can do.",
                "That's a reasonable starting point. Let's negotiate properly.",
                "You know the market well. Let's find common ground."
            ]
        
        return random.choice(responses)
    
    def _clean_response(self, response: str) -> str:
        """Clean and format AI response"""
        # Remove unwanted prefixes
        prefixes = ["AI:", "Seller:", "Response:", "I say:", "I respond:"]
        for prefix in prefixes:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
        
        # Limit to 2 sentences max
        sentences = response.split('.')
        if len(sentences) > 2:
            response = '. '.join(sentences[:2]) + '.'
        
        return response.strip()

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Product:
    """Premium product model"""
    name: str
    category: str
    quantity: int
    quality_grade: str
    origin: str
    base_market_price: int
    seller_min_price: int
    attributes: Dict[str, Any]
    description: str = ""

@dataclass
class NegotiationState:
    """Enhanced negotiation state tracking"""
    product: Product
    human_budget: int
    seller_current_price: int
    human_current_offer: int
    round_number: int
    start_time: float
    time_limit: int
    conversation_history: List[Dict[str, Any]]
    deal_closed: bool
    final_price: Optional[int]
    winner: Optional[str]
    personality_revealed: bool = False

class DealStatus(Enum):
    ONGOING = "ongoing"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    TIMEOUT = "timeout"

# ═══════════════════════════════════════════════════════════════════════════════
# 🎭 ADVANCED AI PERSONALITIES
# ═══════════════════════════════════════════════════════════════════════════════

class AIPersonalities:
    """Advanced AI seller personalities with rich characteristics"""
    
    AGGRESSIVE_TRADER = {
        "name": "Aggressive Market Trader",
        "emoji": "🔥",
        "description": "Fast-paced, profit-focused, creates urgency",
        "opening_multiplier": 1.55,
        "min_concession": 0.02,
        "max_concession": 0.08,
        "timeout_pressure": True,
        "personality_prompt": """You are a high-energy Indian commodity trader who speaks with urgency and confidence. 
        You emphasize premium quality, scarcity, and time pressure. Use phrases like 'premium grade', 'limited stock', 
        'other buyers waiting'. You're direct but not rude. Keep responses under 2 sentences and always push for higher prices.""",
        "signature_phrases": [
            "Premium quality commands premium prices!",
            "Time is money in this business!",
            "Other customers are calling as we speak!",
            "You won't find better quality anywhere!",
            "Limited stock - prices rising daily!"
        ]
    }
    
    DIPLOMATIC_MERCHANT = {
        "name": "Diplomatic Merchant",
        "emoji": "🤝",
        "description": "Relationship-focused, collaborative, seeks win-win deals",
        "opening_multiplier": 1.35,
        "min_concession": 0.04,
        "max_concession": 0.12,
        "timeout_pressure": False,
        "personality_prompt": """You are a patient, relationship-focused Indian merchant who values long-term business. 
        You speak about mutual benefits, fair deals, and building trust. Use phrases like 'win-win', 'fair for both', 
        'long-term relationship'. You're collaborative and understanding. Keep responses professional and warm.""",
        "signature_phrases": [
            "Let's find a mutually beneficial price.",
            "Quality like this builds lasting relationships.",
            "I value our partnership in this deal.",
            "Fair dealing is the foundation of good business.",
            "Together we can make this work perfectly."
        ]
    }
    
    CUNNING_STRATEGIST = {
        "name": "Cunning Market Strategist",
        "emoji": "🧠",
        "description": "Psychological tactics, adaptive, reads buyer behavior",
        "opening_multiplier": 1.45,
        "min_concession": 0.01,
        "max_concession": 0.15,
        "timeout_pressure": True,
        "personality_prompt": """You are a clever Indian merchant who uses psychological tactics and reads buyer behavior. 
        You mention other buyers, compliment the customer, create strategic urgency. Use phrases like 'for someone like you', 
        'I can see you know quality', 'other interested parties'. You're charming but strategic.""",
        "signature_phrases": [
            "Ah, I can see you know real quality!",
            "For a discerning buyer like you...",
            "Other parties are very interested, but...",
            "You have excellent taste in products.",
            "Smart negotiators like you are rare!"
        ]
    }

# ═══════════════════════════════════════════════════════════════════════════════
# 🤖 ENHANCED AI SELLER
# ═══════════════════════════════════════════════════════════════════════════════

class SmartAISeller:
    """Advanced AI seller with personality and intelligence"""
    
    def __init__(self, personality_key: str = "DIPLOMATIC_MERCHANT"):
        self.personality = getattr(AIPersonalities, personality_key)
        self.ai_client = SmartLlamaClient()
        self.negotiation_memory = []
        
    def get_opening_offer(self, product: Product) -> Tuple[int, str]:
        """Generate compelling opening offer"""
        opening_price = int(product.base_market_price * self.personality["opening_multiplier"])
        
        context = f"""
PRODUCT SHOWCASE:
- Product: {product.name} ({product.quality_grade} grade from {product.origin})
- Quantity: {product.quantity} units
- Market Value: ₹{product.base_market_price:,}
- Your Price: ₹{opening_price:,}
- Special Features: {', '.join([f'{k}={v}' for k, v in product.attributes.items()])}

Create an engaging opening pitch that showcases the product value and justifies your price.
"""
        
        ai_response = self.ai_client.generate_response(self.personality["personality_prompt"], context)
        
        # Enhance response with product details and price
        if len(ai_response) < 20:
            signature = random.choice(self.personality["signature_phrases"])
            message = f"Welcome to premium {product.name} from {product.origin}! {signature} My price: ₹{opening_price:,}."
        else:
            message = ai_response
            if f"₹{opening_price:,}" not in message:
                message += f" Price: ₹{opening_price:,}."
        
        return opening_price, message
    
    def respond_to_offer(self, state: NegotiationState, human_offer: int, human_message: str) -> Tuple[DealStatus, int, str]:
        """Generate intelligent response to human offer"""
        product = state.product
        time_remaining = state.time_limit - (time.time() - state.start_time)
        
        # Quick acceptance for excellent offers
        if human_offer >= product.seller_min_price * 1.08:
            return DealStatus.ACCEPTED, human_offer, f"Excellent offer! ₹{human_offer:,} is a deal! 🤝"
        
        # Emergency mode in final seconds
        if time_remaining < 15:
            if human_offer >= product.seller_min_price:
                return DealStatus.ACCEPTED, human_offer, f"Time's up - ₹{human_offer:,} accepted!"
            else:
                emergency_price = max(product.seller_min_price, int(human_offer * 1.02))
                return DealStatus.ONGOING, emergency_price, f"FINAL SECONDS: ₹{emergency_price:,}!"
        
        # Calculate strategic counter-offer
        counter_price = self._calculate_smart_counter(state, human_offer, time_remaining)
        
        # Generate contextual response
        context = self._build_negotiation_context(state, human_offer, counter_price, time_remaining, human_message)
        ai_response = self.ai_client.generate_response(self.personality["personality_prompt"], context)
        
        # Enhance and format response
        final_message = self._enhance_response(ai_response, counter_price, human_offer, time_remaining)
        
        return DealStatus.ONGOING, counter_price, final_message
    
    def _calculate_smart_counter(self, state: NegotiationState, human_offer: int, time_remaining: float) -> int:
        """Calculate intelligent counter-offer"""
        current_price = state.seller_current_price
        gap = current_price - human_offer
        
        # Base concession rate based on round
        base_rate = 0.02 + (state.round_number * 0.015)
        base_rate = min(base_rate, self.personality["max_concession"])
        
        # Time pressure adjustment
        if time_remaining < 60:
            base_rate *= 1.5
        
        # Personality-specific adjustments
        if self.personality["name"] == "Cunning Market Strategist":
            # Analyze human behavior pattern
            recent_offers = [msg.get("offer", 0) for msg in state.conversation_history[-3:] 
                           if msg.get("role") == "human" and "offer" in msg]
            
            if len(recent_offers) >= 2:
                if recent_offers[-1] > recent_offers[-2]:  # Human increasing offers
                    base_rate *= 0.7  # Be more conservative
                elif recent_offers[-1] < recent_offers[-2]:  # Human decreasing
                    base_rate *= 1.3  # Be more generous
        
        # Calculate final concession
        concession = max(2000, int(gap * base_rate))  # Minimum ₹2000 concession
        counter_price = max(state.product.seller_min_price, current_price - concession)
        
        return counter_price
    
    def _build_negotiation_context(self, state: NegotiationState, human_offer: int, counter_price: int, 
                                 time_remaining: float, human_message: str) -> str:
        """Build rich context for AI response"""
        return f"""
CURRENT NEGOTIATION STATUS:
- Round: {state.round_number}
- Time Left: {int(time_remaining)} seconds
- Human Offer: ₹{human_offer:,}
- Your Counter: ₹{counter_price:,}
- Human Said: "{human_message}"
- Product: {state.product.name} ({state.product.quality_grade} grade)

NEGOTIATION HISTORY:
{self._get_conversation_summary(state)}

Respond to their offer with your counter-price. Be engaging and stay in character.
Make them want to buy from you while defending your price point.
"""
    
    def _get_conversation_summary(self, state: NegotiationState) -> str:
        """Get summarized conversation history"""
        recent_msgs = state.conversation_history[-4:]
        summary = ""
        for msg in recent_msgs:
            role = msg["role"].title()
            content = msg.get("message", "")[:50] + "..."
            if "offer" in msg:
                summary += f"{role}: {content} (₹{msg['offer']:,})\n"
            elif "price" in msg:
                summary += f"{role}: {content} (₹{msg['price']:,})\n"
        return summary.strip()
    
    def _enhance_response(self, ai_response: str, counter_price: int, human_offer: int, time_remaining: float) -> str:
        """Enhance AI response with personality touches"""
        # Clean response
        response = ai_response.strip()
        
        # Ensure price is mentioned
        if f"₹{counter_price:,}" not in response and str(counter_price) not in response:
            response += f" I can do ₹{counter_price:,}."
        
        # Add personality flair
        if len(response) < 30:  # Too short, add signature phrase
            signature = random.choice(self.personality["signature_phrases"])
            response = f"{signature} {response}"
        
        # Time pressure for appropriate personalities
        if time_remaining < 45 and self.personality["timeout_pressure"]:
            if time_remaining < 25:
                response += f" ⏰ Only {int(time_remaining)} seconds left!"
            else:
                response += " ⏰ Time is running short!"
        
        return response

# ═══════════════════════════════════════════════════════════════════════════════
# 🏪 PREMIUM PRODUCT CATALOG
# ═══════════════════════════════════════════════════════════════════════════════

class ProductCatalog:
    """Premium product catalog with rich descriptions"""
    
    @staticmethod
    def get_products() -> List[Product]:
        return [
            Product(
                name="Alphonso Mangoes",
                category="Premium Fruits",
                quantity=100,
                quality_grade="Export A+",
                origin="Ratnagiri, Maharashtra",
                base_market_price=220000,
                seller_min_price=175000,
                attributes={"ripeness": "perfect", "certification": "organic", "harvest": "2024"},
                description="The king of mangoes - premium export quality with perfect sweetness"
            ),
            Product(
                name="Basmati Rice",
                category="Premium Grains",
                quantity=500,
                quality_grade="1121 Extra Long",
                origin="Punjab",
                base_market_price=180000,
                seller_min_price=145000,
                attributes={"age": "2_years", "length": "8.2mm", "aroma": "premium"},
                description="Aged premium basmati with exceptional aroma and extra-long grains"
            ),
            Product(
                name="Darjeeling Tea",
                category="Premium Beverages",
                quantity=50,
                quality_grade="FTGFOP1",
                origin="Darjeeling Hills",
                base_market_price=95000,
                seller_min_price=76000,
                attributes={"flush": "second", "estate": "Makaibari", "altitude": "7000ft"},
                description="Finest second flush Darjeeling with muscatel flavor"
            ),
            Product(
                name="Kashmir Saffron",
                category="Premium Spices",
                quantity=10,
                quality_grade="Mongra Grade I",
                origin="Kashmir Valley",
                base_market_price=450000,
                seller_min_price=380000,
                attributes={"crocin": "250+", "purity": "99.9%", "threads": "premium"},
                description="World's finest saffron with highest crocin content"
            ),
            Product(
                name="Kashmiri Walnuts",
                category="Premium Dry Fruits",
                quantity=200,
                quality_grade="Jumbo",
                origin="Kashmir",
                base_market_price=160000,
                seller_min_price=130000,
                attributes={"size": "jumbo", "oil_content": "65%", "harvest": "fresh"},
                description="Premium jumbo walnuts with high oil content and rich flavor"
            )
        ]

# ═══════════════════════════════════════════════════════════════════════════════
# 🎮 MAIN BARGAINING ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class SmartBargainingSystem:
    """Professional bargaining system with enhanced features"""
    
    def __init__(self):
        self.current_negotiation: Optional[NegotiationState] = None
        self.ai_seller: Optional[SmartAISeller] = None
        self.products = ProductCatalog.get_products()
        self.ui = UIManager()
        
    def start_negotiation(self, product_index: int, budget: int, time_limit: int = 120) -> bool:
        """Start professional negotiation session"""
        if product_index >= len(self.products):
            print(f"{Colors.BRIGHT_RED}❌ Invalid product selection!{Colors.RESET}")
            return False
        
        product = self.products[product_index]
        
        # Budget validation with professional feedback
        if budget < product.seller_min_price:
            print(f"\n{Colors.BRIGHT_YELLOW}⚠️  BUDGET ANALYSIS:{Colors.RESET}")
            print(f"{Colors.WHITE}Your Budget: ₹{budget:,}{Colors.RESET}")
            print(f"{Colors.WHITE}Seller Minimum: ~₹{product.seller_min_price:,}{Colors.RESET}")
            print(f"{Colors.BRIGHT_RED}Challenge Level: EXTREME 🔥{Colors.RESET}")
            
            if input(f"\n{Colors.BRIGHT_CYAN}Accept the challenge? (y/n): {Colors.RESET}").lower() != 'y':
                return False
        
        # Randomly select AI personality
        personalities = ["AGGRESSIVE_TRADER", "DIPLOMATIC_MERCHANT", "CUNNING_STRATEGIST"]
        selected_personality = random.choice(personalities)
        self.ai_seller = SmartAISeller(selected_personality)
        
        # Get opening offer
        opening_price, opening_message = self.ai_seller.get_opening_offer(product)
        
        # Initialize negotiation
        self.current_negotiation = NegotiationState(
            product=product,
            human_budget=budget,
            seller_current_price=opening_price,
            human_current_offer=0,
            round_number=1,
            start_time=time.time(),
            time_limit=time_limit,
            conversation_history=[],
            deal_closed=False,
            final_price=None,
            winner=None
        )
        
        # Add opening to history
        self.current_negotiation.conversation_history.append({
            "role": "seller",
            "message": opening_message,
            "price": opening_price,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })
        
        # Display negotiation start
        self._display_negotiation_start(opening_message)
        return True
    
    def _display_negotiation_start(self, opening_message: str):
        """Display professional negotiation start screen"""
        self.ui.clear_screen()
        
        product = self.current_negotiation.product
        
        # Header
        self.ui.print_header("🎯 SMART BARGAIN AI - LIVE NEGOTIATION", "Professional Market Simulation")
        
        # Product showcase
        print(f"\n{Colors.BRIGHT_MAGENTA}📦 FEATURED PRODUCT{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}{product.name} - {product.quality_grade}{Colors.RESET}")
        print(f"{Colors.CYAN}📍 Origin: {product.origin} | Qty: {product.quantity} units{Colors.RESET}")
        print(f"{Colors.YELLOW}💰 Market Value: ₹{product.base_market_price:,}{Colors.RESET}")
        print(f"{Colors.WHITE}✨ {product.description}{Colors.RESET}")
        
        # Your stats
        print(f"\n{Colors.BRIGHT_GREEN}💼 YOUR PROFILE{Colors.RESET}")
        print(f"{Colors.WHITE}Budget: ₹{self.current_negotiation.human_budget:,}{Colors.RESET}")
        print(f"{Colors.WHITE}Time Limit: {self.current_negotiation.time_limit // 60}:{self.current_negotiation.time_limit % 60:02d}{Colors.RESET}")
        
        # AI seller intro (mysterious)
        print(f"\n{Colors.BRIGHT_RED}🤖 AI SELLER PROFILE{Colors.RESET}")
        print(f"{Colors.WHITE}Identity: {Colors.BRIGHT_YELLOW}??? Mystery Trader ???{Colors.RESET}")
        print(f"{Colors.WHITE}Personality will be revealed during negotiation...{Colors.RESET}")
        
        print(f"\n{Colors.BRIGHT_CYAN}{'═' * 80}{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}🤖 AI SELLER: {opening_message}{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{'═' * 80}{Colors.RESET}")
        
        # Show commands hint
        print(f"\n{Colors.BRIGHT_BLUE}💡 QUICK COMMANDS:{Colors.RESET}")
        print(f"{Colors.WHITE}• offer [amount] [message] - Make an offer{Colors.RESET}")
        print(f"{Colors.WHITE}• accept - Accept current offer{Colors.RESET}")
        print(f"{Colors.WHITE}• status - Check negotiation status{Colors.RESET}")
        print(f"{Colors.WHITE}• help - Show all commands{Colors.RESET}")
    
    def make_human_offer(self, offer_amount: int, message: str = "") -> bool:
        """Process human offer with enhanced feedback"""
        if not self.current_negotiation or self.current_negotiation.deal_closed:
            print(f"{Colors.BRIGHT_RED}❌ No active negotiation!{Colors.RESET}")
            return False
        
        # Time check
        elapsed = time.time() - self.current_negotiation.start_time
        if elapsed >= self.current_negotiation.time_limit:
            self._end_negotiation("timeout")
            return False
        
        # Validation
        if offer_amount > self.current_negotiation.human_budget:
            print(f"{Colors.BRIGHT_RED}❌ Offer exceeds budget of ₹{self.current_negotiation.human_budget:,}!{Colors.RESET}")
            return False
        
        if offer_amount <= 0:
            print(f"{Colors.BRIGHT_RED}❌ Invalid offer amount!{Colors.RESET}")
            return False
        
        # Update state
        self.current_negotiation.human_current_offer = offer_amount
        self.current_negotiation.round_number += 1
        
        # Add to history
        self.current_negotiation.conversation_history.append({
            "role": "human",
            "message": message or f"I offer ₹{offer_amount:,}",
            "offer": offer_amount,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })
        
        # Get AI response
        status, seller_price, seller_message = self.ai_seller.respond_to_offer(
            self.current_negotiation, offer_amount, message
        )
        
        # Update seller price
        self.current_negotiation.seller_current_price = seller_price
        
        # Add seller response
        self.current_negotiation.conversation_history.append({
            "role": "seller",
            "message": seller_message,
            "price": seller_price,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })
        
        # Display response with style
        self._display_ai_response(seller_message, seller_price)
        
        # Check for deal acceptance
        if status == DealStatus.ACCEPTED:
            # Reveal personality
            personality = self.ai_seller.personality
            print(f"\n{Colors.BG_GREEN}{Colors.BLACK} 🎭 PERSONALITY REVEALED: {personality['name']} {personality['emoji']} {Colors.RESET}")
            self._end_negotiation("deal", seller_price)
            return True
        
        # Show current status
        self._display_mini_status()
        return True
    
    def _display_ai_response(self, message: str, price: int):
        """Display AI response with visual flair"""
        # Reveal personality after round 3
        if self.current_negotiation.round_number >= 3 and not self.current_negotiation.personality_revealed:
            personality = self.ai_seller.personality
            print(f"\n{Colors.BRIGHT_YELLOW}🎭 PERSONALITY REVEALED: {personality['name']} {personality['emoji']}{Colors.RESET}")
            print(f"{Colors.WHITE}{personality['description']}{Colors.RESET}")
            self.current_negotiation.personality_revealed = True
        
        print(f"\n{Colors.BRIGHT_RED}🤖 AI SELLER:{Colors.RESET}")
        self.ui.animate_text(f"{Colors.BRIGHT_WHITE}{message}{Colors.RESET}", 0.02)
        
        if price > 0:
            print(f"{Colors.BRIGHT_YELLOW}💰 Current Price: ₹{price:,}{Colors.RESET}")
    
    def _display_mini_status(self):
        """Show compact status during negotiation"""
        elapsed = time.time() - self.current_negotiation.start_time
        remaining = max(0, self.current_negotiation.time_limit - elapsed)
        
        print(f"\n{Colors.BRIGHT_BLUE}📊 STATUS:{Colors.RESET} ", end="")
        self.ui.print_timer(int(remaining))
        print(f"| Round: {self.current_negotiation.round_number} | Your Offer: ₹{self.current_negotiation.human_current_offer:,}")
        print(f"{Colors.BRIGHT_CYAN}{'─' * 60}{Colors.RESET}")
    
    def accept_seller_offer(self) -> bool:
        """Accept current seller offer with style"""
        if not self.current_negotiation or self.current_negotiation.deal_closed:
            print(f"{Colors.BRIGHT_RED}❌ No active negotiation!{Colors.RESET}")
            return False
        
        final_price = self.current_negotiation.seller_current_price
        
        if final_price > self.current_negotiation.human_budget:
            print(f"{Colors.BRIGHT_RED}❌ Price exceeds your budget!{Colors.RESET}")
            return False
        
        # Add acceptance to history
        self.current_negotiation.conversation_history.append({
            "role": "human",
            "message": f"I accept your offer of ₹{final_price:,}!",
            "offer": final_price,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })
        
        print(f"\n{Colors.BRIGHT_GREEN}✅ You accepted ₹{final_price:,}!{Colors.RESET}")
        
        # Reveal personality if not already
        if not self.current_negotiation.personality_revealed:
            personality = self.ai_seller.personality
            print(f"{Colors.BRIGHT_YELLOW}🎭 You were negotiating with: {personality['name']} {personality['emoji']}{Colors.RESET}")
        
        self._end_negotiation("deal", final_price)
        return True
    
    def reject_negotiation(self) -> bool:
        """Reject and exit with style"""
        if not self.current_negotiation:
            return False
        
        personality = self.ai_seller.personality
        print(f"\n{Colors.BRIGHT_RED}❌ You walked away from the negotiation!{Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}🎭 You were facing: {personality['name']} {personality['emoji']}{Colors.RESET}")
        
        self._end_negotiation("rejected")
        return True
    
    def _end_negotiation(self, result: str, final_price: int = None):
        """End negotiation with comprehensive results"""
        if not self.current_negotiation:
            return
        
        self.current_negotiation.deal_closed = True
        self.current_negotiation.final_price = final_price
        
        duration = time.time() - self.current_negotiation.start_time
        
        # Clear screen for results
        self.ui.clear_screen()
        
        if result == "deal" and final_price:
            self._display_success_results(final_price, duration)
        elif result == "timeout":
            self._display_timeout_results(duration)
        elif result == "rejected":
            self._display_rejection_results(duration)
    
    def _display_success_results(self, final_price: int, duration: float):
        """Display successful deal results"""
        self.ui.print_header("🎉 DEAL SUCCESSFUL! 🎉", "Congratulations on Your Negotiation!")
        
        # Calculate savings and performance
        budget_savings = self.current_negotiation.human_budget - final_price
        market_savings = self.current_negotiation.product.base_market_price - final_price
        market_discount = (market_savings / self.current_negotiation.product.base_market_price) * 100
        
        # Deal summary
        print(f"\n{Colors.BRIGHT_GREEN}💰 DEAL SUMMARY{Colors.RESET}")
        print(f"{Colors.WHITE}Final Price: ₹{final_price:,}{Colors.RESET}")
        print(f"{Colors.WHITE}Your Budget: ₹{self.current_negotiation.human_budget:,}{Colors.RESET}")
        print(f"{Colors.WHITE}Budget Savings: ₹{budget_savings:,}{Colors.RESET}")
        print(f"{Colors.WHITE}Market Savings: ₹{market_savings:,} ({market_discount:.1f}% off){Colors.RESET}")
        
        # Performance rating
        if market_discount >= 20:
            rating = f"{Colors.BG_GREEN}{Colors.BLACK} OUTSTANDING DEAL! 🏆 {Colors.RESET}"
        elif market_discount >= 10:
            rating = f"{Colors.BG_BLUE}{Colors.WHITE} EXCELLENT DEAL! 👏 {Colors.RESET}"
        elif market_discount >= 5:
            rating = f"{Colors.BG_YELLOW}{Colors.BLACK} GOOD DEAL! 👍 {Colors.RESET}"
        else:
            rating = f"{Colors.BG_CYAN}{Colors.BLACK} FAIR DEAL! ✅ {Colors.RESET}"
        
        print(f"\n{rating}")
        
        # Negotiation stats
        print(f"\n{Colors.BRIGHT_BLUE}📊 NEGOTIATION STATS{Colors.RESET}")
        print(f"{Colors.WHITE}Duration: {duration:.1f} seconds{Colors.RESET}")
        print(f"{Colors.WHITE}Rounds: {self.current_negotiation.round_number}{Colors.RESET}")
        print(f"{Colors.WHITE}AI Personality: {self.ai_seller.personality['name']}{Colors.RESET}")
    
    def _display_timeout_results(self, duration: float):
        """Display timeout results"""
        self.ui.print_header("⏰ TIME'S UP! ⏰", "Negotiation Timed Out")
        
        print(f"\n{Colors.BRIGHT_RED}No deal was reached within the time limit.{Colors.RESET}")
        print(f"{Colors.WHITE}Duration: {duration:.1f} seconds{Colors.RESET}")
        print(f"{Colors.WHITE}Rounds Completed: {self.current_negotiation.round_number}{Colors.RESET}")
        print(f"{Colors.WHITE}AI Personality: {self.ai_seller.personality['name']}{Colors.RESET}")
        
        # Show what could have been
        if self.current_negotiation.seller_current_price <= self.current_negotiation.human_budget:
            missed_deal = self.current_negotiation.seller_current_price
            print(f"\n{Colors.BRIGHT_YELLOW}💔 You could have gotten it for ₹{missed_deal:,}!{Colors.RESET}")
    
    def _display_rejection_results(self, duration: float):
        """Display rejection results"""
        self.ui.print_header("❌ NEGOTIATION ENDED ❌", "You Chose to Walk Away")
        
        print(f"\n{Colors.BRIGHT_RED}Sometimes walking away is the best decision.{Colors.RESET}")
        print(f"{Colors.WHITE}Duration: {duration:.1f} seconds{Colors.RESET}")
        print(f"{Colors.WHITE}Rounds: {self.current_negotiation.round_number}{Colors.RESET}")
        print(f"{Colors.WHITE}AI Personality: {self.ai_seller.personality['name']}{Colors.RESET}")
    
    def show_products(self):
        """Display enhanced product catalog"""
        self.ui.clear_screen()
        self.ui.print_header("📦 PREMIUM PRODUCT CATALOG", "Select Your Negotiation Target")
        
        for i, product in enumerate(self.products):
            print(f"\n{Colors.BRIGHT_MAGENTA}═══ {i}. {product.name} ═══{Colors.RESET}")
            print(f"{Colors.BRIGHT_WHITE}Category: {product.category} | Grade: {product.quality_grade}{Colors.RESET}")
            print(f"{Colors.CYAN}📍 Origin: {product.origin} | Quantity: {product.quantity} units{Colors.RESET}")
            print(f"{Colors.YELLOW}💰 Market Price: ₹{product.base_market_price:,}{Colors.RESET}")
            print(f"{Colors.WHITE}✨ {product.description}{Colors.RESET}")
            print(f"{Colors.BRIGHT_BLUE}Specs: {', '.join([f'{k}={v}' for k, v in product.attributes.items()])}{Colors.RESET}")
        
        print(f"\n{Colors.BRIGHT_CYAN}{'═' * 80}{Colors.RESET}")
    
    def show_status(self):
        """Display current negotiation status"""
        if not self.current_negotiation:
            print(f"{Colors.BRIGHT_RED}❌ No active negotiation!{Colors.RESET}")
            return
        
        elapsed = time.time() - self.current_negotiation.start_time
        remaining = max(0, self.current_negotiation.time_limit - elapsed)
        
        print(f"\n{Colors.BRIGHT_BLUE}📊 DETAILED STATUS{Colors.RESET}")
        print(f"{Colors.WHITE}Product: {self.current_negotiation.product.name}{Colors.RESET}")
        print(f"{Colors.WHITE}Your Budget: ₹{self.current_negotiation.human_budget:,}{Colors.RESET}")
        print(f"{Colors.WHITE}Current AI Price: ₹{self.current_negotiation.seller_current_price:,}{Colors.RESET}")
        print(f"{Colors.WHITE}Your Last Offer: ₹{self.current_negotiation.human_current_offer:,}{Colors.RESET}")
        print(f"{Colors.WHITE}Round: {self.current_negotiation.round_number}{Colors.RESET}")
        
        print(f"\n{Colors.BRIGHT_YELLOW}⏰ Time Remaining: ", end="")
        self.ui.print_timer(int(remaining))
        print()
        
        if self.current_negotiation.personality_revealed:
            personality = self.ai_seller.personality
            print(f"{Colors.BRIGHT_MAGENTA}🎭 AI Personality: {personality['name']} {personality['emoji']}{Colors.RESET}")

# ═══════════════════════════════════════════════════════════════════════════════
# 🎮 COMMAND LINE INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def parse_command(command: str, system: SmartBargainingSystem) -> bool:
    """Parse and execute user commands"""
    parts = command.strip().lower().split()
    
    if not parts:
        return True
    
    cmd = parts[0]
    
    if cmd == "offer":
        if len(parts) < 2:
            print(f"{Colors.BRIGHT_RED}❌ Usage: offer [amount] [optional message]{Colors.RESET}")
            return True
        
        try:
            amount = int(parts[1])
            message = " ".join(parts[2:]) if len(parts) > 2 else ""
            return system.make_human_offer(amount, message)
        except ValueError:
            print(f"{Colors.BRIGHT_RED}❌ Invalid amount!{Colors.RESET}")
            return True
    
    elif cmd == "accept":
        return system.accept_seller_offer()
    
    elif cmd == "reject" or cmd == "quit" or cmd == "exit":
        return system.reject_negotiation()
    
    elif cmd == "status":
        system.show_status()
        return True
    
    elif cmd == "help":
        show_help()
        return True
    
    else:
        print(f"{Colors.BRIGHT_RED}❌ Unknown command. Type 'help' for available commands.{Colors.RESET}")
        return True

def show_help():
    """Show command help"""
    print(f"\n{Colors.BRIGHT_BLUE}🎯 AVAILABLE COMMANDS{Colors.RESET}")
    print(f"{Colors.WHITE}offer [amount] [message] - Make an offer (e.g., 'offer 150000 This is my best offer'){Colors.RESET}")
    print(f"{Colors.WHITE}accept                  - Accept the current AI offer{Colors.RESET}")
    print(f"{Colors.WHITE}reject/quit/exit        - End negotiation and walk away{Colors.RESET}")
    print(f"{Colors.WHITE}status                  - Show detailed negotiation status{Colors.RESET}")
    print(f"{Colors.WHITE}help                    - Show this help message{Colors.RESET}")
    
    print(f"\n{Colors.BRIGHT_YELLOW}💡 NEGOTIATION TIPS:{Colors.RESET}")
    print(f"{Colors.WHITE}• Start with a reasonable offer, not too low{Colors.RESET}")
    print(f"{Colors.WHITE}• Watch the timer - AI behavior changes under time pressure{Colors.RESET}")
    print(f"{Colors.WHITE}• AI personality reveals after round 3{Colors.RESET}")
    print(f"{Colors.WHITE}• Each AI has different negotiation patterns{Colors.RESET}")

def run_negotiation(system: SmartBargainingSystem):
    """Run the interactive negotiation loop"""
    while system.current_negotiation and not system.current_negotiation.deal_closed:
        # Check for timeout
        elapsed = time.time() - system.current_negotiation.start_time
        if elapsed >= system.current_negotiation.time_limit:
            system._end_negotiation("timeout")
            break
        
        try:
            command = input(f"\n{Colors.BRIGHT_CYAN}💬 Your move: {Colors.RESET}").strip()
            
            if not command:
                continue
            
            # Process command
            if not parse_command(command, system):
                break
                
        except KeyboardInterrupt:
            print(f"\n\n{Colors.BRIGHT_YELLOW}Negotiation interrupted!{Colors.RESET}")
            system.reject_negotiation()
            break
        except EOFError:
            print(f"\n\n{Colors.BRIGHT_YELLOW}Session ended!{Colors.RESET}")
            break

def start_negotiation_flow(system: SmartBargainingSystem):
    """Enhanced negotiation startup flow"""
    # Show products
    system.show_products()
    
    # Get selections
    try:
        product_idx = int(input(f"\n{Colors.BRIGHT_CYAN}Select product (0-{len(system.products)-1}): {Colors.RESET}"))
        if product_idx < 0 or product_idx >= len(system.products):
            print(f"{Colors.BRIGHT_RED}❌ Invalid selection!{Colors.RESET}")
            return
    except ValueError:
        print(f"{Colors.BRIGHT_RED}❌ Please enter a valid number!{Colors.RESET}")
        return
    
    # Get budget
    try:
        budget = int(input(f"{Colors.BRIGHT_CYAN}Enter your budget (₹): {Colors.RESET}"))
        if budget <= 0:
            print(f"{Colors.BRIGHT_RED}❌ Budget must be positive!{Colors.RESET}")
            return
    except ValueError:
        print(f"{Colors.BRIGHT_RED}❌ Please enter a valid budget!{Colors.RESET}")
        return
    
    # Optional: Custom time limit
    try:
        time_choice = input(f"{Colors.BRIGHT_CYAN}Time limit (120s default, or enter custom): {Colors.RESET}").strip()
        time_limit = int(time_choice) if time_choice else 120
        if time_limit < 30:
            time_limit = 30
        if time_limit > 300:
            time_limit = 300
    except ValueError:
        time_limit = 120
    
    # Start negotiation
    if system.start_negotiation(product_idx, budget, time_limit):
        run_negotiation(system)
    
    # Post-negotiation
    input(f"\n{Colors.BRIGHT_CYAN}Press Enter to return to main menu...{Colors.RESET}")

# ═══════════════════════════════════════════════════════════════════════════════
# 🎮 MAIN GAME INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main game interface with professional styling"""
    system = SmartBargainingSystem()
    ui = UIManager()
    
    # Welcome screen
    ui.clear_screen()
    ui.print_header("🎯 SMART BARGAIN AI", "Professional AI-Powered Negotiation System")
    
    print(f"\n{Colors.BRIGHT_GREEN}🚀 POWERED BY LLAMA 3.1 8B{Colors.RESET}")
    print(f"{Colors.WHITE}• Intelligent AI responses with personality{Colors.RESET}")
    print(f"{Colors.WHITE}• Real-time market simulation{Colors.RESET}")
    print(f"{Colors.WHITE}• Professional negotiation training{Colors.RESET}")
    print(f"{Colors.WHITE}• Mystery AI personalities to discover{Colors.RESET}")
    
    print(f"\n{Colors.BRIGHT_YELLOW}⚡ QUICK START GUIDE{Colors.RESET}")
    print(f"{Colors.WHITE}1. Choose a premium product{Colors.RESET}")
    print(f"{Colors.WHITE}2. Set your budget{Colors.RESET}")
    print(f"{Colors.WHITE}3. Negotiate with mystery AI trader{Colors.RESET}")
    print(f"{Colors.WHITE}4. Close the best deal possible!{Colors.RESET}")
    
    while True:
        print(f"\n{Colors.BRIGHT_CYAN}🎯 MAIN MENU{Colors.RESET}")
        print(f"{Colors.WHITE}1. 🚀 Start New Negotiation{Colors.RESET}")
        print(f"{Colors.WHITE}2. 📦 Browse Product Catalog{Colors.RESET}")
        print(f"{Colors.WHITE}3. 🎭 View AI Personalities{Colors.RESET}")
        print(f"{Colors.WHITE}4. ❌ Exit{Colors.RESET}")
        
        choice = input(f"\n{Colors.BRIGHT_BLUE}Select option (1-4): {Colors.RESET}").strip()
        
        if choice == "1":
            start_negotiation_flow(system)
        elif choice == "2":
            system.show_products()
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")
        elif choice == "3":
            show_ai_personalities()
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")
        elif choice == "4":
            ui.clear_screen()
            print(f"{Colors.BRIGHT_GREEN}Thanks for using Smart Bargain AI! 🎯{Colors.RESET}")
            print(f"{Colors.WHITE}Master the art of negotiation! 🤝{Colors.RESET}")
            break
        else:
            print(f"{Colors.BRIGHT_RED}❌ Invalid choice!{Colors.RESET}")

def show_ai_personalities():
    """Display AI personality information"""
    ui = UIManager()
    ui.clear_screen()
    ui.print_header("🎭 AI PERSONALITY GUIDE", "Know Your Opponents")
    
    personalities = [
        AIPersonalities.AGGRESSIVE_TRADER,
        AIPersonalities.DIPLOMATIC_MERCHANT,
        AIPersonalities.CUNNING_STRATEGIST
    ]
    
    for i, personality in enumerate(personalities):
        print(f"\n{Colors.BRIGHT_MAGENTA}═══ {personality['name']} {personality['emoji']} ═══{Colors.RESET}")
        print(f"{Colors.WHITE}{personality['description']}{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLUE}Strategy:{Colors.RESET}")
        print(f"{Colors.CYAN}• Opening Price: {personality['opening_multiplier']}x market rate{Colors.RESET}")
        print(f"{Colors.CYAN}• Concession Range: {personality['min_concession']*100:.0f}%-{personality['max_concession']*100:.0f}%{Colors.RESET}")
        print(f"{Colors.CYAN}• Time Pressure: {'Yes' if personality['timeout_pressure'] else 'No'}{Colors.RESET}")
        
        print(f"{Colors.BRIGHT_YELLOW}Signature Phrases:{Colors.RESET}")
        for phrase in personality['signature_phrases'][:3]:
            print(f"{Colors.WHITE}• \"{phrase}\"{Colors.RESET}")
        
        if i < len(personalities) - 1:
            print(f"{Colors.BRIGHT_CYAN}{'─' * 60}{Colors.RESET}")

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 APPLICATION ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BRIGHT_YELLOW}Program interrupted. Goodbye! 👋{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.BRIGHT_RED}❌ Unexpected error: {e}{Colors.RESET}")
        print(f"{Colors.WHITE}Please report this issue for debugging.{Colors.RESET}")
    finally:
        print(f"{Colors.RESET}")  # Reset colors