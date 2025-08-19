"""
===========================================
HUMAN vs AI SELLER BARGAINING SYSTEM
Powered by Llama 3.1 8B via Ollama
===========================================

A real-time negotiation system where you (human buyer) bargain with an AI seller.
The AI seller uses Llama 3.1 8B for intelligent, context-aware responses.
Time limit: 2 minutes per negotiation.
"""

import json
import time
import threading
import random
import requests
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import datetime

# ============================================
# DATA STRUCTURES
# ============================================

@dataclass
class Product:
    """Product being negotiated"""
    name: str
    category: str
    quantity: int
    quality_grade: str  # 'A', 'B', or 'Export'
    origin: str
    base_market_price: int
    seller_min_price: int  # Seller's absolute minimum
    attributes: Dict[str, Any]

@dataclass
class NegotiationState:
    """Current negotiation state"""
    product: Product
    human_budget: int
    seller_current_price: int
    human_current_offer: int
    round_number: int
    start_time: float
    time_limit: int  # seconds
    conversation_history: List[Dict[str, str]]
    deal_closed: bool
    final_price: Optional[int]
    winner: Optional[str]

class DealStatus(Enum):
    ONGOING = "ongoing"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    TIMEOUT = "timeout"

# ============================================
# LLAMA 3.1 INTEGRATION
# ============================================

class LlamaClient:
    """Client for communicating with Llama 3.1 via Ollama"""
    
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.model = "llama3.1:8b"
        self._test_connection()
    
    def _test_connection(self):
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model["name"] for model in models]
                if not any("llama3.1" in name for name in model_names):
                    print("⚠️  Warning: Llama 3.1 not found. Please run: ollama pull llama3.1:8b")
                else:
                    print("✅ Connected to Ollama with Llama 3.1!")
            else:
                raise ConnectionError("Ollama server not responding")
        except Exception as e:
            print(f"❌ Cannot connect to Ollama: {e}")
            print("📋 Setup Instructions:")
            print("   1. Install Ollama: https://ollama.ai/")
            print("   2. Run: ollama pull llama3.1:8b")
            print("   3. Ensure Ollama is running on localhost:11434")
            print("   4. Restart this program")
            exit(1)
    
    def generate_response(self, prompt: str, max_tokens: int = 200) -> str:
        """Generate response using Llama 3.1"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "max_tokens": max_tokens,
                    "stop": ["Human:", "Buyer:", "\n\n"]
                }
            }
            
            response = requests.post(
                f"{self.host}/api/generate", 
                json=payload, 
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                return "I need a moment to think... How about we continue?"
                
        except Exception as e:
            print(f"⚠️  Llama error: {e}")
            return "Let me reconsider... What's your next offer?"

# ============================================
# AI SELLER PERSONALITIES (Enhanced for Llama)
# ============================================

class AISellerPersonality:
    """Different AI seller personalities"""
    
    AGGRESSIVE = {
        "name": "Aggressive Dealer",
        "traits": ["impatient", "profit-focused", "direct"],
        "opening_multiplier": 1.6,  # 60% above market
        "min_concession": 0.02,  # 2% minimum concession
        "max_concession": 0.08,  # 8% maximum concession
        "timeout_pressure": True,
        "system_prompt": """You are an AGGRESSIVE Indian fruit/commodity dealer. You are impatient, profit-focused, and direct. 
        You speak with urgency, use phrases like "time is money", "decide quickly", "premium quality". 
        You're pushy but not rude. You emphasize scarcity and time pressure. Keep responses under 2 sentences.
        You're selling to make maximum profit and don't like long negotiations.""",
        "phrases": [
            "This is premium quality, my friend!",
            "Time is money - decide quickly!",
            "You won't find better elsewhere!",
            "My final offer - take it or leave it!",
            "Other customers are waiting!"
        ]
    }
    
    DIPLOMATIC = {
        "name": "Diplomatic Trader",
        "traits": ["patient", "relationship-builder", "smooth-talker"],
        "opening_multiplier": 1.4,  # 40% above market
        "min_concession": 0.03,  # 3% minimum concession
        "max_concession": 0.12,  # 12% maximum concession
        "timeout_pressure": False,
        "system_prompt": """You are a DIPLOMATIC Indian commodity trader. You are patient, relationship-focused, and smooth-talking.
        You speak politely, use phrases like "mutual benefit", "fair deal for both", "let's work together".
        You're collaborative and emphasize long-term relationships. Keep responses under 2 sentences.
        You prefer win-win situations and build trust with customers.""",
        "phrases": [
            "Let's find a price that works for both of us.",
            "I appreciate your interest in our products.",
            "Perhaps we can reach a mutually beneficial agreement.",
            "Quality like this speaks for itself.",
            "I'm confident we can make this work."
        ]
    }
    
    CUNNING = {
        "name": "Cunning Merchant",
        "traits": ["strategic", "psychological", "adaptive"],
        "opening_multiplier": 1.5,  # 50% above market
        "min_concession": 0.01,  # 1% minimum concession
        "max_concession": 0.15,  # 15% maximum concession (but strategic)
        "timeout_pressure": True,
        "system_prompt": """You are a CUNNING Indian merchant. You are strategic, use psychological tactics, and adapt to buyers.
        You mention other buyers, create urgency, compliment the buyer, use phrases like "special price for you", "limited stock".
        You're clever and manipulative but charming. Keep responses under 2 sentences.
        You read the buyer's behavior and adjust your strategy accordingly.""",
        "phrases": [
            "Ah, I see you know quality when you see it!",
            "Other buyers are also interested...",
            "For someone like you, I might consider...",
            "This price won't last long!",
            "You drive a hard bargain, but I respect that."
        ]
    }

# ============================================
# AI SELLER AGENT
# ============================================

class AISellerAgent:
    """Intelligent AI seller powered by Llama 3.1 that negotiates with human buyers"""
    
    def __init__(self, personality_type: str = "DIPLOMATIC"):
        self.personality = getattr(AISellerPersonality, personality_type)
        self.llama_client = LlamaClient()
        self.negotiation_history = []
        
    def _create_negotiation_prompt(self, context: str, human_offer: int = None, human_message: str = "") -> str:
        """Create contextual prompt for Llama 3.1"""
        base_prompt = f"""
{self.personality['system_prompt']}

CURRENT SITUATION:
{context}

NEGOTIATION CONTEXT:
- You must respond as a seller trying to get the best price
- Stay in character as a {self.personality['name']}
- Be realistic about Indian commodity pricing (use ₹ symbol)
- Keep responses conversational and under 2 sentences
- Include your counter-price in your response
"""
        
        if human_offer and human_message:
            base_prompt += f"""
HUMAN BUYER JUST SAID: "{human_message}" and offered ₹{human_offer:,}

Your response should:
1. React to their offer and message
2. Make a counter-offer with your new price
3. Stay in character
4. Be concise but persuasive

Respond as the seller:"""
        else:
            base_prompt += f"""
This is the opening of the negotiation. Make your opening offer and introduce the product.

Respond as the seller:"""
        
        return base_prompt
        
    def get_opening_offer(self, product: Product) -> Tuple[int, str]:
        """Generate opening price and message using Llama 3.1"""
        opening_price = int(product.base_market_price * self.personality["opening_multiplier"])
        
        context = f"""
Product: {product.name} ({product.quality_grade} grade from {product.origin})
Quantity: {product.quantity} units
Market Price: ₹{product.base_market_price:,}
Your Opening Price: ₹{opening_price:,}
Attributes: {', '.join([f'{k}={v}' for k, v in product.attributes.items()])}
"""
        
        prompt = self._create_negotiation_prompt(context)
        
        # Get AI response
        ai_response = self.llama_client.generate_response(prompt)
        
        # Clean and format response
        message = ai_response.replace("₹", "").strip()
        if not message or len(message) < 10:
            # Fallback to preset phrases if AI fails
            greeting = f"Welcome! I have excellent {product.quality_grade} grade {product.name} from {product.origin}."
            phrase = random.choice(self.personality["phrases"])
            message = f"{greeting} {phrase} My price is ₹{opening_price:,}."
        else:
            # Ensure price is mentioned
            if f"₹{opening_price:,}" not in message and f"{opening_price}" not in message:
                message += f" My price is ₹{opening_price:,}."
        
        return opening_price, message
    
    def respond_to_human_offer(self, state: NegotiationState, human_offer: int, human_message: str = "") -> Tuple[DealStatus, int, str]:
        """Generate AI response to human offer using Llama 3.1"""
        product = state.product
        time_remaining = state.time_limit - (time.time() - state.start_time)
        
        # Check if human offer meets minimum (accept immediately)
        if human_offer >= product.seller_min_price * 1.05:  # 5% profit margin
            acceptance_phrases = [
                f"Excellent! You have a deal at ₹{human_offer:,}!",
                f"I accept your offer of ₹{human_offer:,}. Pleasure doing business!",
                f"Agreed! ₹{human_offer:,} it is. You won't regret this purchase!"
            ]
            return DealStatus.ACCEPTED, human_offer, random.choice(acceptance_phrases)
        
        # Emergency acceptance if time is running out
        if time_remaining < 20:  # Last 20 seconds
            if human_offer >= product.seller_min_price:
                return DealStatus.ACCEPTED, human_offer, "Time's up - I'll take your offer!"
            else:
                final_price = max(product.seller_min_price, int(human_offer * 1.01))
                return DealStatus.ONGOING, final_price, f"FINAL SECONDS - ₹{final_price:,}!"
        
        # Calculate strategic counter-offer
        counter_price = self._calculate_counter_offer(state, human_offer)
        
        # Create context for Llama
        context = f"""
Product: {product.name} ({product.quality_grade} grade, {product.quantity} units)
Market Price: ₹{product.base_market_price:,}
Your Current Price: ₹{state.seller_current_price:,}
Human's Offer: ₹{human_offer:,}
Your Counter-Price: ₹{counter_price:,}
Round: {state.round_number}
Time Remaining: {int(time_remaining)} seconds

Previous conversation:
{self._get_recent_conversation(state, 3)}
"""
        
        prompt = self._create_negotiation_prompt(context, human_offer, human_message)
        
        # Get AI response
        ai_response = self.llama_client.generate_response(prompt, max_tokens=150)
        
        # Process and clean the AI response
        message = self._process_ai_response(ai_response, counter_price, human_offer, time_remaining)
        
        return DealStatus.ONGOING, counter_price, message
    
    def _calculate_counter_offer(self, state: NegotiationState, human_offer: int) -> int:
        """Calculate strategic counter-offer based on personality and situation"""
        current_price = state.seller_current_price
        gap = current_price - human_offer
        product = state.product
        
        # Determine concession rate based on round and personality
        if state.round_number <= 2:
            concession_rate = self.personality["min_concession"]
        elif state.round_number >= 6:
            concession_rate = self.personality["max_concession"]
        else:
            concession_rate = self.personality["min_concession"] + (
                (self.personality["max_concession"] - self.personality["min_concession"]) * 
                (state.round_number - 2) / 4
            )
        
        # Apply personality-specific adjustments
        if self.personality["name"] == "Cunning Merchant":
            # Cunning merchant adapts based on human behavior
            recent_offers = [msg.get("offer", 0) for msg in state.conversation_history[-3:] 
                           if msg["role"] == "human" and "offer" in msg]
            if len(recent_offers) >= 2 and recent_offers[-1] > recent_offers[-2]:
                concession_rate *= 0.6  # Reduce concession if human is increasing offers
        
        # Calculate concession
        concession = max(1000, int(gap * concession_rate))  # Minimum ₹1000 concession
        counter_price = max(product.seller_min_price, current_price - concession)
        
        return counter_price
    
    def _get_recent_conversation(self, state: NegotiationState, num_messages: int) -> str:
        """Get recent conversation for context"""
        recent = state.conversation_history[-num_messages:]
        conversation = ""
        for msg in recent:
            role = msg["role"].title()
            if "offer" in msg:
                conversation += f"{role}: {msg['message']} (₹{msg['offer']:,})\n"
            elif "price" in msg:
                conversation += f"{role}: {msg['message']} (₹{msg['price']:,})\n"
            else:
                conversation += f"{role}: {msg['message']}\n"
        return conversation.strip()
    
    def _process_ai_response(self, ai_response: str, counter_price: int, human_offer: int, time_remaining: float) -> str:
        """Process and enhance AI response"""
        # Clean the response
        message = ai_response.strip()
        
        # Remove any unwanted prefixes
        prefixes_to_remove = ["Seller:", "AI:", "Response:", "I respond:", "As a seller:"]
        for prefix in prefixes_to_remove:
            if message.startswith(prefix):
                message = message[len(prefix):].strip()
        
        # Ensure the response isn't too long
        sentences = message.split('.')
        if len(sentences) > 2:
            message = '. '.join(sentences[:2]) + '.'
        
        # Ensure price is mentioned clearly
        if f"₹{counter_price:,}" not in message and f"{counter_price}" not in message:
            message += f" I can do ₹{counter_price:,}."
        
        # Add time pressure if needed
        if time_remaining < 45 and self.personality["timeout_pressure"]:
            if time_remaining < 30:
                message += f" Only {int(time_remaining)} seconds left!"
            else:
                message += " Time is running short!"
        
        # Fallback if response is too short or generic
        if len(message) < 15:
            fallback_messages = [
                f"₹{human_offer:,}? I can come down to ₹{counter_price:,}.",
                f"That's quite low. How about ₹{counter_price:,}?",
                f"I can do ₹{counter_price:,} - that's my best offer!"
            ]
            message = random.choice(fallback_messages)
        
        return message

# ============================================
# MAIN BARGAINING SYSTEM
# ============================================

class BargainingSystem:
    """Main system that manages human-AI negotiations"""
    
    def __init__(self):
        self.current_negotiation: Optional[NegotiationState] = None
        self.seller_agent = None
        self.products_catalog = self._load_products()
        
    def _load_products(self) -> List[Product]:
        """Load available products for negotiation"""
        return [
            Product(
                name="Alphonso Mangoes",
                category="Mangoes",
                quantity=100,
                quality_grade="Export",
                origin="Ratnagiri",
                base_market_price=200000,
                seller_min_price=160000,
                attributes={"ripeness": "perfect", "export_quality": True, "organic": True}
            ),
            Product(
                name="Basmati Rice",
                category="Grains",
                quantity=500,
                quality_grade="A",
                origin="Punjab",
                base_market_price=150000,
                seller_min_price=125000,
                attributes={"age": "1_year", "aroma": "premium", "length": "extra_long"}
            ),
            Product(
                name="Darjeeling Tea",
                category="Beverages",
                quantity=50,
                quality_grade="Export",
                origin="West Bengal",
                base_market_price=75000,
                seller_min_price=60000,
                attributes={"flush": "second", "estate": "premium", "processing": "orthodox"}
            ),
            Product(
                name="Red Chilli",
                category="Spices",
                quantity=200,
                quality_grade="A",
                origin="Andhra Pradesh",
                base_market_price=80000,
                seller_min_price=65000,
                attributes={"scoville": "25000", "moisture": "8%", "color": "deep_red"}
            ),
            Product(
                name="Cotton",
                category="Textiles",
                quantity=1000,
                quality_grade="B",
                origin="Gujarat",
                base_market_price=120000,
                seller_min_price=95000,
                attributes={"staple_length": "28mm", "micronaire": "4.2", "strength": "high"}
            )
        ]
    
    def start_new_negotiation(self, product_index: int, human_budget: int, seller_personality: str = "DIPLOMATIC", time_limit: int = 120) -> bool:
        """Start a new negotiation session"""
        if product_index >= len(self.products_catalog):
            print("❌ Invalid product selection!")
            return False
            
        if human_budget <= 0:
            print("❌ Invalid budget!")
            return False
        
        product = self.products_catalog[product_index]
        
        # Check if budget is reasonable
        if human_budget < product.seller_min_price:
            print(f"⚠️  Warning: Your budget (₹{human_budget:,}) is below seller's minimum (₹{product.seller_min_price:,})")
            proceed = input("Continue anyway? (y/n): ").lower() == 'y'
            if not proceed:
                return False
        
        # Initialize seller agent
        self.seller_agent = AISellerAgent(seller_personality)
        
        # Get seller's opening offer
        opening_price, opening_message = self.seller_agent.get_opening_offer(product)
        
        # Initialize negotiation state
        self.current_negotiation = NegotiationState(
            product=product,
            human_budget=human_budget,
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
        
        # Add opening message to history
        self.current_negotiation.conversation_history.append({
            "role": "seller",
            "message": opening_message,
            "price": opening_price,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })
        
        print(f"\n🤝 NEGOTIATION STARTED!")
        print(f"⏱️  Time Limit: {time_limit} seconds")
        print(f"💰 Your Budget: ₹{human_budget:,}")
        print(f"📦 Product: {product.name} ({product.quantity} units, {product.quality_grade} grade)")
        print(f"🏪 Market Price: ₹{product.base_market_price:,}")
        print("=" * 60)
        print(f"🤖 Mystery AI Seller: {opening_message}")
        print("=" * 60)
        print("💡 Tip: Try to figure out the seller's personality from their responses!")
        
        return True
    
    def human_make_offer(self, offer_amount: int, message: str = "") -> bool:
        """Process human's offer"""
        if not self.current_negotiation or self.current_negotiation.deal_closed:
            print("❌ No active negotiation!")
            return False
        
        # Check time limit
        elapsed_time = time.time() - self.current_negotiation.start_time
        if elapsed_time >= self.current_negotiation.time_limit:
            self._end_negotiation("timeout")
            return False
        
        # Validate offer
        if offer_amount > self.current_negotiation.human_budget:
            print(f"❌ Offer exceeds your budget of ₹{self.current_negotiation.human_budget:,}!")
            return False
        
        if offer_amount <= 0:
            print("❌ Invalid offer amount!")
            return False
        
        # Update state
        self.current_negotiation.human_current_offer = offer_amount
        self.current_negotiation.round_number += 1
        
        # Add to conversation history
        self.current_negotiation.conversation_history.append({
            "role": "human",
            "message": message or f"I offer ₹{offer_amount:,}",
            "offer": offer_amount,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })
        
        # Get AI response
        status, seller_price, seller_message = self.seller_agent.respond_to_human_offer(
            self.current_negotiation, offer_amount, message
        )
        
        # Update seller price
        self.current_negotiation.seller_current_price = seller_price
        
        # Add seller response to history
        self.current_negotiation.conversation_history.append({
            "role": "seller",
            "message": seller_message,
            "price": seller_price,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })
        
        # Display response with personality reveal after 3 rounds
        if self.current_negotiation.round_number >= 3:
            print(f"🤖 AI Seller ({self.seller_agent.personality['name']}): {seller_message}")
        else:
            print(f"🤖 AI Seller: {seller_message}")
        
        # Check if deal is accepted
        if status == DealStatus.ACCEPTED:
            # Reveal personality on deal closure
            print(f"🎭 PERSONALITY REVEALED: You were negotiating with a {self.seller_agent.personality['name']}!")
            self._end_negotiation("deal", seller_price)
            return True
        
        # Show current status
        self._show_current_status()
        
        return True
    
    def accept_seller_offer(self) -> bool:
        """Human accepts current seller offer"""
        if not self.current_negotiation or self.current_negotiation.deal_closed:
            print("❌ No active negotiation!")
            return False
        
        final_price = self.current_negotiation.seller_current_price
        
        if final_price > self.current_negotiation.human_budget:
            print(f"❌ Cannot accept - price exceeds your budget!")
            return False
        
        self.current_negotiation.conversation_history.append({
            "role": "human",
            "message": f"I accept your offer of ₹{final_price:,}!",
            "offer": final_price,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })
        
        print(f"✅ You accepted the seller's offer of ₹{final_price:,}!")
        self._end_negotiation("deal", final_price)
        return True
    
    def reject_and_exit(self) -> bool:
        """Human rejects and exits negotiation"""
        if not self.current_negotiation:
            return False
        
        print("❌ You rejected the negotiation and walked away.")
        self._end_negotiation("rejected")
        return True
    
    def _show_current_status(self):
        """Display current negotiation status"""
        if not self.current_negotiation:
            return
        
        elapsed = time.time() - self.current_negotiation.start_time
        remaining = max(0, self.current_negotiation.time_limit - elapsed)
        
        print(f"\n📊 CURRENT STATUS:")
        print(f"⏱️  Time Remaining: {int(remaining)} seconds")
        print(f"🔄 Round: {self.current_negotiation.round_number}")
        print(f"🤖 Seller's Price: ₹{self.current_negotiation.seller_current_price:,}")
        print(f"👤 Your Last Offer: ₹{self.current_negotiation.human_current_offer:,}")
        print(f"💰 Your Budget: ₹{self.current_negotiation.human_budget:,}")
        print("-" * 40)
    
    def _end_negotiation(self, result: str, final_price: int = None):
        """End the current negotiation"""
        if not self.current_negotiation:
            return
        
        self.current_negotiation.deal_closed = True
        self.current_negotiation.final_price = final_price
        
        end_time = time.time()
        duration = end_time - self.current_negotiation.start_time
        
        print(f"\n🏁 NEGOTIATION ENDED!")
        print(f"⏱️  Duration: {duration:.1f} seconds")
        print(f"🔄 Rounds: {self.current_negotiation.round_number}")
        
        if result == "deal" and final_price:
            savings = self.current_negotiation.human_budget - final_price
            market_savings = self.current_negotiation.product.base_market_price - final_price
            
            print(f"✅ DEAL SUCCESSFUL!")
            print(f"💰 Final Price: ₹{final_price:,}")
            print(f"💵 You Saved: ₹{savings:,} from your budget")
            print(f"📈 Market Savings: ₹{market_savings:,} ({market_savings/self.current_negotiation.product.base_market_price*100:.1f}%)")
            
            if final_price <= self.current_negotiation.product.base_market_price * 0.8:
                print("🏆 EXCELLENT DEAL! You got it for 20% below market price!")
            elif final_price <= self.current_negotiation.product.base_market_price * 0.9:
                print("👏 GOOD DEAL! You got it for 10% below market price!")
            else:
                print("✅ FAIR DEAL! Close to market price.")
                
            self.current_negotiation.winner = "human"
            
        elif result == "timeout":
            print("⏰ TIMEOUT! Negotiation ended without a deal.")
            print(f"🎭 PERSONALITY REVEALED: You were facing a {self.seller_agent.personality['name']}!")
            self.current_negotiation.winner = "timeout"
            
        elif result == "rejected":
            print("❌ NEGOTIATION REJECTED!")
            print(f"🎭 PERSONALITY REVEALED: You walked away from a {self.seller_agent.personality['name']}!")
            self.current_negotiation.winner = "no_deal"
        
        print("=" * 60)
    
    def show_conversation_history(self):
        """Display complete conversation history"""
        if not self.current_negotiation:
            print("No negotiation in progress.")
            return
        
        print(f"\n💬 CONVERSATION HISTORY:")
        print("=" * 60)
        
        for i, msg in enumerate(self.current_negotiation.conversation_history, 1):
            role_icon = "🤖" if msg["role"] == "seller" else "👤"
            print(f"{i}. [{msg['timestamp']}] {role_icon} {msg['role'].title()}: {msg['message']}")
            
        print("=" * 60)
    
    def get_available_products(self) -> List[Dict]:
        """Get list of available products"""
        return [
            {
                "index": i,
                "name": product.name,
                "category": product.category,
                "quantity": product.quantity,
                "quality": product.quality_grade,
                "origin": product.origin,
                "market_price": product.base_market_price,
                "attributes": product.attributes
            }
            for i, product in enumerate(self.products_catalog)
        ]

# ============================================
# COMMAND LINE INTERFACE
# ============================================

def main():
    """Main CLI interface for the bargaining system"""
    system = BargainingSystem()
    
    print("🤖 POWERED BY LLAMA 3.1 8B - AI SELLER BARGAINING SYSTEM!")
    print("=" * 60)
    print("💡 Tips:")
    print("   • You have 2 minutes to negotiate")
    print("   • Stay within your budget")
    print("   • Each AI seller has a mystery personality!")
    print("   • The AI uses Llama 3.1 for intelligent responses")
    print("   • Try to figure out their strategy from their responses")
    print("   • Type 'help' for commands during negotiation")
    print("=" * 60)
    print("📋 SETUP REQUIREMENTS:")
    print("   • Ollama must be installed and running")
    print("   • Run: ollama pull llama3.1:8b")
    print("   • Ensure localhost:11434 is accessible")
    print("=" * 60)
    
    while True:
        print(f"\n📋 MAIN MENU:")
        print("1. Start New Negotiation")
        print("2. View Available Products")
        print("3. Exit")
        
        choice = input("Choose option (1-3): ").strip()
        
        if choice == "1":
            start_negotiation_flow(system)
        elif choice == "2":
            show_products(system)
        elif choice == "3":
            print("👋 Thanks for using the bargaining system!")
            break
        else:
            print("❌ Invalid choice!")

def start_negotiation_flow(system: BargainingSystem):
    """Handle negotiation startup flow"""
    # Show available products
    products = system.get_available_products()
    print(f"\n📦 AVAILABLE PRODUCTS:")
    print("-" * 60)
    for product in products:
        print(f"{product['index']}. {product['name']} ({product['quality']} grade)")
        print(f"   📍 Origin: {product['origin']} | 📦 Qty: {product['quantity']} units")
        print(f"   💰 Market Price: ₹{product['market_price']:,}")
        print()
    
    # Get product selection
    try:
        product_idx = int(input("Select product (number): "))
        if product_idx >= len(products):
            print("❌ Invalid product selection!")
            return
    except ValueError:
        print("❌ Invalid input!")
        return
    
    # Get budget
    try:
        budget = int(input("Enter your budget (₹): "))
        if budget <= 0:
            print("❌ Invalid budget!")
            return
    except ValueError:
        print("❌ Invalid budget amount!")
        return
    
    # Randomly select AI personality for surprise challenge
    personalities = ["DIPLOMATIC", "AGGRESSIVE", "CUNNING"]
    personality = random.choice(personalities)
    print(f"\n🎲 AI Seller personality will be revealed during negotiation...")
    
    # Start negotiation
    if system.start_new_negotiation(product_idx, budget, personality, 120):
        run_negotiation_loop(system)

def run_negotiation_loop(system: BargainingSystem):
    """Run the main negotiation interaction loop"""
    print(f"\n💬 NEGOTIATION COMMANDS:")
    print("• offer [amount] [message] - Make an offer")
    print("• accept - Accept seller's current offer")
    print("• reject - Reject and exit negotiation")
    print("• status - Show current status")
    print("• history - Show conversation history")
    print("• help - Show this help")
    print()
    
    while system.current_negotiation and not system.current_negotiation.deal_closed:
        # Check for timeout
        elapsed = time.time() - system.current_negotiation.start_time
        if elapsed >= system.current_negotiation.time_limit:
            system._end_negotiation("timeout")
            break
        
        remaining = system.current_negotiation.time_limit - elapsed
        print(f"\n⏱️  [{int(remaining)}s remaining] Your move:")
        
        user_input = input(">>> ").strip().lower()
        
        if not user_input:
            continue
        
        parts = user_input.split()
        command = parts[0]
        
        if command == "offer":
            if len(parts) < 2:
                print("❌ Usage: offer [amount] [optional message]")
                continue
            
            try:
                amount = int(parts[1])
                message = " ".join(parts[2:]) if len(parts) > 2 else ""
                system.human_make_offer(amount, message)
            except ValueError:
                print("❌ Invalid offer amount!")
        
        elif command == "accept":
            system.accept_seller_offer()
        
        elif command == "reject":
            system.reject_and_exit()
        
        elif command == "status":
            system._show_current_status()
        
        elif command == "history":
            system.show_conversation_history()
        
        elif command == "help":
            print("💬 COMMANDS:")
            print("• offer [amount] [message] - Make an offer")
            print("• accept - Accept seller's current offer")
            print("• reject - Reject and exit negotiation")
            print("• status - Show current status")
            print("• history - Show conversation history")
        
        else:
            print("❌ Unknown command. Type 'help' for available commands.")

def show_products(system: BargainingSystem):
    """Display detailed product information"""
    products = system.get_available_products()
    print(f"\n📦 PRODUCT CATALOG:")
    print("=" * 80)
    
    for product in products:
        print(f"{product['index']}. {product['name']} - {product['category']}")
        print(f"   📍 Origin: {product['origin']}")
        print(f"   🏷️  Quality: {product['quality']} grade")
        print(f"   📦 Quantity: {product['quantity']} units")
        print(f"   💰 Market Price: ₹{product['market_price']:,}")
        print(f"   ✨ Attributes: {', '.join([f'{k}={v}' for k, v in product['attributes'].items()])}")
        print()
    
    print("=" * 80)

if __name__ == "__main__":
    main()