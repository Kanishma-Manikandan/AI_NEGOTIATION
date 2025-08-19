"""
===========================================
HUMAN vs AI SELLER BARGAINING SYSTEM
===========================================

A real-time negotiation system where you (human buyer) bargain with an AI seller.
Time limit: 2 minutes per negotiation.
"""

import json
import time
import threading
import random
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
# AI SELLER PERSONALITIES
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
        "phrases": [
            "This is a premium product, my friend!",
            "I'm already giving you a great deal!",
            "Time is money - decide quickly!",
            "You won't find better quality elsewhere!",
            "My final offer - take it or leave it!"
        ]
    }
    
    DIPLOMATIC = {
        "name": "Diplomatic Trader",
        "traits": ["patient", "relationship-builder", "smooth-talker"],
        "opening_multiplier": 1.4,  # 40% above market
        "min_concession": 0.03,  # 3% minimum concession
        "max_concession": 0.12,  # 12% maximum concession
        "timeout_pressure": False,
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
    """Intelligent AI seller that negotiates with human buyers"""
    
    def __init__(self, personality_type: str = "DIPLOMATIC"):
        self.personality = getattr(AISellerPersonality, personality_type)
        self.negotiation_history = []
        
    def get_opening_offer(self, product: Product) -> Tuple[int, str]:
        """Generate opening price and message"""
        opening_price = int(product.base_market_price * self.personality["opening_multiplier"])
        
        greeting = random.choice([
            f"Welcome! I have excellent {product.quality_grade} grade {product.name} from {product.origin}.",
            f"You've come to the right place for premium {product.name}!",
            f"These {product.name} are the finest {product.quality_grade} grade you'll find!"
        ])
        
        phrase = random.choice(self.personality["phrases"])
        message = f"{greeting} {phrase} My price is ₹{opening_price:,} for {product.quantity} units."
        
        return opening_price, message
    
    def respond_to_human_offer(self, state: NegotiationState, human_offer: int, human_message: str = "") -> Tuple[DealStatus, int, str]:
        """Generate AI response to human offer"""
        product = state.product
        time_remaining = state.time_limit - (time.time() - state.start_time)
        
        # Check if human offer meets minimum
        if human_offer >= product.seller_min_price * 1.05:  # 5% profit margin
            acceptance_phrases = [
                f"Excellent! You have a deal at ₹{human_offer:,}!",
                f"I accept your offer of ₹{human_offer:,}. Pleasure doing business!",
                f"Agreed! ₹{human_offer:,} it is. You won't regret this purchase!"
            ]
            return DealStatus.ACCEPTED, human_offer, random.choice(acceptance_phrases)
        
        # Time pressure logic
        if time_remaining < 30:  # Last 30 seconds
            if human_offer >= product.seller_min_price:
                return DealStatus.ACCEPTED, human_offer, "Time's running out - I'll take your offer!"
            else:
                final_price = max(product.seller_min_price, int(human_offer * 1.02))
                return DealStatus.ONGOING, final_price, f"FINAL OFFER - ₹{final_price:,}! Only seconds left!"
        
        # Calculate counter-offer based on personality
        current_price = state.seller_current_price
        gap = current_price - human_offer
        
        # Determine concession based on round and personality
        if state.round_number <= 2:
            concession_rate = self.personality["min_concession"]
        elif state.round_number >= 6:
            concession_rate = self.personality["max_concession"]
        else:
            concession_rate = self.personality["min_concession"] + (
                (self.personality["max_concession"] - self.personality["min_concession"]) * 
                (state.round_number - 2) / 4
            )
        
        # Apply some randomness and strategy
        if self.personality["name"] == "Cunning Merchant":
            # Cunning merchant adapts based on human behavior
            if len(state.conversation_history) > 2:
                last_human_offers = [int(msg.get("offer", 0)) for msg in state.conversation_history[-3:] if msg["role"] == "human" and "offer" in msg]
                if len(last_human_offers) >= 2 and last_human_offers[-1] > last_human_offers[-2]:
                    concession_rate *= 0.5  # Reduce concession if human is increasing offers
        
        concession = int(gap * concession_rate)
        counter_price = max(product.seller_min_price, current_price - concession)
        
        # Generate contextual message
        message = self._generate_response_message(state, human_offer, counter_price, time_remaining)
        
        return DealStatus.ONGOING, counter_price, message
    
    def _generate_response_message(self, state: NegotiationState, human_offer: int, counter_price: int, time_remaining: float) -> str:
        """Generate contextual response message"""
        personality_phrase = random.choice(self.personality["phrases"])
        
        # Different message types based on situation
        if human_offer < state.product.base_market_price * 0.7:
            # Very low offer
            messages = [
                f"₹{human_offer:,}? That's far too low for {state.product.quality_grade} grade products! {personality_phrase}",
                f"I'm afraid ₹{human_offer:,} doesn't reflect the true value. How about ₹{counter_price:,}?",
                f"You're asking me to sell at a loss! ₹{counter_price:,} is more reasonable."
            ]
        elif abs(counter_price - human_offer) < 5000:
            # Close to agreement
            messages = [
                f"We're getting close! I can do ₹{counter_price:,}. {personality_phrase}",
                f"Almost there - ₹{counter_price:,} and we have a deal!",
                f"You're a tough negotiator! ₹{counter_price:,} is my best offer."
            ]
        else:
            # Normal negotiation
            messages = [
                f"I can come down to ₹{counter_price:,}. {personality_phrase}",
                f"For you, ₹{counter_price:,}. That's cutting into my margins!",
                f"₹{counter_price:,} - and that's a significant discount already."
            ]
        
        # Add time pressure if needed
        if time_remaining < 60 and self.personality["timeout_pressure"]:
            time_pressure = random.choice([
                f" Only {int(time_remaining)} seconds left!",
                " Time is running out!",
                " Better decide quickly!"
            ])
            messages = [msg + time_pressure for msg in messages]
        
        return random.choice(messages)

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
        print(f"🤖 AI Seller ({self.seller_agent.personality['name']}): {opening_message}")
        print("=" * 60)
        
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
        
        # Display response
        print(f"🤖 AI Seller: {seller_message}")
        
        # Check if deal is accepted
        if status == DealStatus.ACCEPTED:
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
            self.current_negotiation.winner = "timeout"
            
        elif result == "rejected":
            print("❌ NEGOTIATION REJECTED!")
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
    
    print("🛒 WELCOME TO THE AI SELLER BARGAINING SYSTEM!")
    print("=" * 60)
    print("💡 Tips:")
    print("   • You have 2 minutes to negotiate")
    print("   • Stay within your budget")
    print("   • Different AI personalities react differently")
    print("   • Type 'help' for commands during negotiation")
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
    
    # Choose AI personality
    print(f"\n🤖 AI SELLER PERSONALITIES:")
    print("1. Diplomatic Trader (Balanced, relationship-focused)")
    print("2. Aggressive Dealer (Direct, profit-focused)")
    print("3. Cunning Merchant (Strategic, adaptive)")
    
    personality_map = {"1": "DIPLOMATIC", "2": "AGGRESSIVE", "3": "CUNNING"}
    personality_choice = input("Choose AI personality (1-3, default=1): ").strip() or "1"
    personality = personality_map.get(personality_choice, "DIPLOMATIC")
    
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