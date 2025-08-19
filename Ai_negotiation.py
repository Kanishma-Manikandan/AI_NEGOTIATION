"""
===========================================
AI NEGOTIATION CONVERSATION SYSTEM
===========================================

This extends your negotiation template with a full conversation system
that allows buyer and seller agents to negotiate naturally.
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
import random

# ============================================
# EXISTING DATA STRUCTURES
# ============================================

@dataclass
class Product:
    """Product being negotiated"""
    name: str
    category: str
    quantity: int
    quality_grade: str  # 'A', 'B', or 'Export'
    origin: str
    base_market_price: int  # Reference price for this product
    attributes: Dict[str, Any]

@dataclass
class NegotiationContext:
    """Current negotiation state"""
    product: Product
    your_budget: int  # Your maximum budget (NEVER exceed this)
    current_round: int
    seller_offers: List[int]  # History of seller's offers
    your_offers: List[int]  # History of your offers
    messages: List[Dict[str, str]]  # Full conversation history

class DealStatus(Enum):
    ONGOING = "ongoing"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    TIMEOUT = "timeout"

# ============================================
# CONVERSATION SYSTEM ENHANCEMENTS
# ============================================

@dataclass
class ConversationTurn:
    """Represents a single turn in the conversation"""
    speaker: str  # "buyer" or "seller"
    message: str
    price_offer: Optional[int]
    round_number: int
    timestamp: str
    deal_status: DealStatus

class ConversationManager:
    """Manages the full conversation flow between buyer and seller"""
    
    def __init__(self, buyer_agent, seller_agent, product: Product, buyer_budget: int):
        self.buyer_agent = buyer_agent
        self.seller_agent = seller_agent
        self.product = product
        self.buyer_budget = buyer_budget
        self.conversation_history = []
        self.round_number = 0
        self.deal_status = DealStatus.ONGOING
        self.final_price = None
        
        # Initialize negotiation context
        self.context = NegotiationContext(
            product=product,
            your_budget=buyer_budget,
            current_round=0,
            seller_offers=[],
            your_offers=[],
            messages=[]
        )
    
    def start_conversation(self) -> List[ConversationTurn]:
        """Start the negotiation conversation"""
        print(f"\n{'='*60}")
        print(f"NEGOTIATION STARTED")
        print(f"Product: {self.product.name} ({self.product.quality_grade} grade)")
        print(f"Quantity: {self.product.quantity} boxes")
        print(f"Market Price: ₹{self.product.base_market_price:,}")
        print(f"Buyer Budget: ₹{self.buyer_budget:,}")
        print(f"{'='*60}\n")
        
        # Seller opens with initial offer
        seller_price, seller_message = self.seller_agent.get_opening_price(self.product)
        self._add_turn("seller", seller_message, seller_price)
        
        # Start negotiation loop
        max_rounds = 10
        while self.deal_status == DealStatus.ONGOING and self.round_number < max_rounds:
            self.round_number += 1
            self.context.current_round = self.round_number
            
            # Buyer responds
            if self.round_number == 1:
                buyer_offer, buyer_message = self.buyer_agent.generate_opening_offer(self.context)
                self.deal_status = DealStatus.ONGOING
            else:
                last_seller_price = self.context.seller_offers[-1] if self.context.seller_offers else None
                last_seller_msg = self._get_last_message("seller")
                self.deal_status, buyer_offer, buyer_message = self.buyer_agent.respond_to_seller_offer(
                    self.context, last_seller_price, last_seller_msg
                )
            
            self._add_turn("buyer", buyer_message, buyer_offer)
            
            if self.deal_status == DealStatus.ACCEPTED:
                self.final_price = self.context.seller_offers[-1] if self.context.seller_offers else buyer_offer
                break
            
            # Seller responds
            seller_price, seller_message, seller_accepts = self.seller_agent.respond_to_buyer(
                buyer_offer, self.round_number
            )
            
            if seller_accepts:
                self.deal_status = DealStatus.ACCEPTED
                self.final_price = buyer_offer
                self._add_turn("seller", seller_message, seller_price)
                break
            else:
                self._add_turn("seller", seller_message, seller_price)
        
        # Handle timeout
        if self.deal_status == DealStatus.ONGOING:
            self.deal_status = DealStatus.TIMEOUT
            self._add_turn("system", "Negotiation timed out after 10 rounds.", None)
        
        self._print_final_summary()
        return self.conversation_history
    
    def _add_turn(self, speaker: str, message: str, price_offer: Optional[int]):
        """Add a conversation turn and update context"""
        turn = ConversationTurn(
            speaker=speaker,
            message=message,
            price_offer=price_offer,
            round_number=self.round_number,
            timestamp=f"Round {self.round_number}",
            deal_status=self.deal_status
        )
        
        self.conversation_history.append(turn)
        
        # Update context
        if speaker == "seller" and price_offer:
            self.context.seller_offers.append(price_offer)
        elif speaker == "buyer" and price_offer:
            self.context.your_offers.append(price_offer)
        
        self.context.messages.append({"role": speaker, "message": message})
        
        # Print the turn
        self._print_turn(turn)
    
    def _print_turn(self, turn: ConversationTurn):
        """Print a conversation turn in a formatted way"""
        speaker_label = "🛒 BUYER" if turn.speaker == "buyer" else "🏪 SELLER" if turn.speaker == "seller" else "⚠️  SYSTEM"
        price_info = f" (₹{turn.price_offer:,})" if turn.price_offer else ""
        
        print(f"{speaker_label}{price_info}:")
        print(f"  {turn.message}")
        print()
    
    def _get_last_message(self, speaker: str) -> str:
        """Get the last message from a specific speaker"""
        for turn in reversed(self.conversation_history):
            if turn.speaker == speaker:
                return turn.message
        return ""
    
    def _print_final_summary(self):
        """Print negotiation results"""
        print(f"{'='*60}")
        print(f"NEGOTIATION COMPLETE - {self.deal_status.value.upper()}")
        
        if self.deal_status == DealStatus.ACCEPTED:
            savings = self.buyer_budget - self.final_price
            savings_pct = (savings / self.buyer_budget) * 100
            market_discount = ((self.product.base_market_price - self.final_price) / self.product.base_market_price) * 100
            
            print(f"✅ Deal Closed at: ₹{self.final_price:,}")
            print(f"💰 Buyer Savings: ₹{savings:,} ({savings_pct:.1f}% of budget)")
            print(f"📊 Below Market Price: {market_discount:.1f}%")
            print(f"🔄 Rounds Completed: {self.round_number}")
        else:
            print(f"❌ No deal reached")
            print(f"🔄 Rounds Completed: {self.round_number}")
        
        print(f"{'='*60}\n")

# ============================================
# ENHANCED SELLER AGENTS
# ============================================

class AdvancedSellerAgent:
    """More sophisticated seller with different strategies"""
    
    def __init__(self, min_price: int, strategy: str = "balanced"):
        self.min_price = min_price
        self.strategy = strategy
        self.negotiation_history = []
        self.rounds_passed = 0
        
    def get_opening_price(self, product: Product) -> Tuple[int, str]:
        """Generate opening offer based on strategy"""
        if self.strategy == "aggressive":
            price = int(product.base_market_price * 1.8)
            message = f"Premium {product.quality_grade}-grade {product.name} from {product.origin}. My price is ₹{price} - this is top quality merchandise."
        elif self.strategy == "conservative":
            price = int(product.base_market_price * 1.3)
            message = f"I have {product.quantity} boxes of {product.quality_grade}-grade {product.name}. Fair price is ₹{price}."
        else:  # balanced
            price = int(product.base_market_price * 1.5)
            message = f"These are excellent {product.quality_grade}-grade {product.name} from {product.origin}. I'm asking ₹{price} for {product.quantity} boxes."
        
        return price, message
    
    def respond_to_buyer(self, buyer_offer: int, round_num: int) -> Tuple[int, str, bool]:
        """Respond to buyer's offer based on strategy"""
        self.rounds_passed = round_num
        
        # Check if we should accept
        profit_margin = (buyer_offer - self.min_price) / self.min_price
        
        if self.strategy == "aggressive":
            accept_threshold = 0.15  # Want 15% profit
            concession_rate = 0.08
        elif self.strategy == "conservative":
            accept_threshold = 0.05  # Accept 5% profit
            concession_rate = 0.12
        else:  # balanced
            accept_threshold = 0.10  # Want 10% profit
            concession_rate = 0.10
        
        # Accept if good profit or late in negotiation
        if profit_margin >= accept_threshold or (round_num >= 8 and buyer_offer >= self.min_price):
            return buyer_offer, f"Excellent! I accept your offer of ₹{buyer_offer:,}. You drive a fair bargain!", True
        
        # Calculate counter-offer
        if round_num >= 9:  # Final round pressure
            counter = max(self.min_price, int(buyer_offer * 1.02))
            message = f"This is my final offer: ₹{counter:,}. I cannot go lower - take it or leave it."
        elif round_num >= 7:  # Late stage
            counter = max(self.min_price, int(buyer_offer * (1 + concession_rate/2)))
            message = f"We're close to a deal. How about ₹{counter:,}? This is nearly my bottom line."
        else:  # Early/mid stage
            counter = max(self.min_price, int(buyer_offer * (1 + concession_rate)))
            message = self._generate_counter_message(counter, round_num)
        
        return counter, message, False
    
    def _generate_counter_message(self, counter_price: int, round_num: int) -> str:
        """Generate contextual counter-offer messages"""
        messages = [
            f"I appreciate your interest, but ₹{counter_price:,} is more realistic for this quality.",
            f"Let me come down to ₹{counter_price:,} - that's a fair compromise.",
            f"I can work with ₹{counter_price:,}. These are premium products after all.",
            f"How about we meet at ₹{counter_price:,}? I'm trying to be flexible here."
        ]
        
        if round_num >= 5:
            messages.extend([
                f"We're spending a lot of time on this. ₹{counter_price:,} and let's close the deal.",
                f"I'm being very generous at ₹{counter_price:,}. Can we agree on this?"
            ])
        
        return random.choice(messages)

# ============================================
# YOUR BUYER AGENT (FROM TEMPLATE)
# ============================================

class YourBuyerAgent:
    """
    Seductive Universal Buyer Agent:
    - Universal seductive style applied to all products and scenarios.
    - Rich conversational messages: flattery, rapport-building, persuasive framing.
    - Safe negotiation: never exceeds budget; adaptive concession schedule; final-round fallback.
    - Opponent modeling: light estimate of seller minimum to inform late-round decisions.
    """

    # Hyperparameters — easy to tune
    MIN_STEP = 1000
    FAR_STEP_RATIO = 0.08
    CLOSE_STEP_RATIO = 0.03
    ESTIMATE_DECAY = 0.80

    def __init__(self, name: str):
        self.name = name
        self.personality = self.define_personality()

    def define_personality(self) -> Dict[str, Any]:
        return {
            "personality_type": "seductive_universal",
            "traits": ["persuasive", "flattering", "calm", "strategic"],
            "negotiation_style": (
                "Uses charm and reason together: flatters the seller, references market logic, "
                "and makes adaptive concessions to close deals while staying within budget."
            ),
            "catchphrases": [
                "You have exquisite taste.",
                "Imagine us both walking away satisfied.",
                "Let's make this a delightful partnership."
            ]
        }

    # ----------------- Helper methods -----------------
    def _init_state(self, context: NegotiationContext):
        if not hasattr(self, "_state"):
            self._state = {
                "seller_history": [],
                "seller_min_est": None,
                "times_seen": 0
            }

    def _update_seller_model(self, seller_price: int):
        s = self._state
        s["times_seen"] += 1
        s["seller_history"].append(seller_price)
        if s["seller_min_est"] is None:
            # start optimistic but reasonable
            s["seller_min_est"] = int(seller_price * 0.9)
        else:
            # move estimate slowly toward observed offers (conservative)
            candidate = int(seller_price * 0.85)
            s["seller_min_est"] = int(self.ESTIMATE_DECAY * s["seller_min_est"] + (1 - self.ESTIMATE_DECAY) * candidate)

    def _quality_opening_multiplier(self, grade: str) -> float:
        g = (grade or "").upper()
        if "EXPORT" in g:
            return 0.82
        if g == "A":
            return 0.80
        if g == "B":
            return 0.76
        return 0.78

    def _quality_walkaway_multiplier(self, grade: str) -> float:
        g = (grade or "").upper()
        if "EXPORT" in g:
            return 0.96
        if g == "A":
            return 0.94
        if g == "B":
            return 0.90
        return 0.92

    def _bounds(self, context: NegotiationContext) -> Tuple[int, int]:
        market = context.product.base_market_price
        opening = int(market * self._quality_opening_multiplier(context.product.quality_grade))
        walkaway = int(market * self._quality_walkaway_multiplier(context.product.quality_grade))
        opening = min(opening, context.your_budget)
        walkaway = min(walkaway, context.your_budget)
        opening = min(opening, walkaway)
        return opening, walkaway

    def _format_seductive(self, content: str) -> str:
        # weave cute/flattering preface and charming closing lines
        pre = random.choice([
            "You have exquisite taste —",
            "I truly admire your offer —",
            "There's something captivating about dealing with you —",
            "Your reputation precedes you —"
        ])
        close = random.choice([
            "Shall we make this a beautiful story to tell?",
            "Let's seal this elegant agreement.",
            "Imagine our future collaborations — promising, isn't it?",
            "This could be the start of something delightful."
        ])
        return f"{pre} {content} {close}"

    def generate_opening_offer(self, context: NegotiationContext) -> Tuple[int, str]:
        """
        Opening: seductive + justified number.
        Start at a quality-adjusted fraction of market (never above budget).
        """
        self._init_state(context)
        market = context.product.base_market_price
        opening, walkaway = self._bounds(context)

        qty = context.product.quantity
        name = context.product.name

        content = (
            f"For {qty} boxes of {context.product.quality_grade}-grade {name}, "
            f"I propose an opening of ₹{opening:,}. It reflects quality, logistics, "
            f"and a sincere wish to build a pleasant partnership."
        )
        message = self._format_seductive(content)
        return opening, message

    def respond_to_seller_offer(self, context: NegotiationContext, seller_price: int, seller_message: str) -> Tuple[DealStatus, int, str]:
        """
        Main negotiation logic:
        - Update opponent model
        - Accept when seller_price is within dynamic target & budget
        - Counter with seductive phrasing and adaptive step sizes otherwise
        """
        self._init_state(context)

        # update model
        if seller_price is not None:
            self._update_seller_model(seller_price)

        market = context.product.base_market_price
        opening, walkaway = self._bounds(context)
        last_my = context.your_offers[-1] if context.your_offers else opening

        # compute round-based target: convex schedule from opening->walkaway over 10 rounds
        rnd = max(1, min(10, context.current_round))
        progress = (rnd - 1) / 9.0
        eased = progress ** 1.2
        round_target = int(opening + (walkaway - opening) * eased)

        # Final-round fallback: accept if seller <= budget
        if context.current_round >= 10 and seller_price is not None and seller_price <= context.your_budget:
            content = f"I will accept ₹{seller_price:,} given the timing — it honors both our positions."
            return DealStatus.ACCEPTED, seller_price, self._format_seductive(content)

        # Accept if seller price <= round target and within budget
        if seller_price is not None and seller_price <= round_target and seller_price <= context.your_budget:
            content = f"That price of ₹{seller_price:,} falls within my fair target for this round — I accept."
            return DealStatus.ACCEPTED, seller_price, self._format_seductive(content)

        # Late-round acceptance if seller_price <= estimated seller_min (defensive)
        est_min = self._state.get("seller_min_est")
        if context.current_round >= 8 and seller_price is not None and est_min is not None:
            if seller_price <= max(est_min, int(walkaway)) and seller_price <= context.your_budget:
                content = f"Given we are close to closing and the figures look sensible, I can accept ₹{seller_price:,}."
                return DealStatus.ACCEPTED, seller_price, self._format_seductive(content)

        # Otherwise compute counter-offer.
        if seller_price is None:
            # no explicit seller price — make a small seductive nudge
            proposed = min(context.your_budget, int(last_my * 1.05))
            proposed = max(proposed, opening)
            content = f"I am inclined toward ₹{proposed:,} — it's a graceful step closer."
            return DealStatus.ONGOING, proposed, self._format_seductive(content)

        # pct gap (seller vs us)
        pct_gap = (seller_price - last_my) / max(1, last_my)
        market_far_step = int(max(self.MIN_STEP, market * self.FAR_STEP_RATIO))
        market_close_step = int(max(self.MIN_STEP, market * self.CLOSE_STEP_RATIO))

        if pct_gap > 0.12:
            step = market_far_step
        elif pct_gap > 0.04:
            step = int((market_far_step + market_close_step) / 2)
        else:
            step = market_close_step

        # Aim toward seller but keep bargaining power
        if seller_price > last_my:
            proposed = min(context.your_budget, last_my + max(step, int((seller_price - last_my) * 0.5)))
        else:
            proposed = max(opening, min(context.your_budget, seller_price - self.MIN_STEP))

        # enforce sensible bounds
        proposed = max(proposed, opening, last_my)
        proposed = min(proposed, context.your_budget, walkaway)

        if proposed == last_my and proposed + self.MIN_STEP <= context.your_budget:
            proposed += self.MIN_STEP

        # Compose seductive justification with some data flavor
        content = (
            f"I can make ₹{proposed:,} for these {context.product.quantity} boxes of "
            f"{context.product.quality_grade}-grade {context.product.name}. "
            "It balances fair margin and promptness — a win for both of us."
        )

        if context.current_round >= 8:
            content += " We are near close; let's be generous to each other and finalize."

        message = self._format_seductive(content)
        return DealStatus.ONGOING, proposed, message

# ============================================
# CONVERSATION TESTING SYSTEM
# ============================================

def run_full_conversation(buyer_strategy: str = "seductive", seller_strategy: str = "balanced"):
    """Run a complete negotiation conversation"""
    
    # Create test product
    product = Product(
        name="Alphonso Mangoes",
        category="Mangoes",
        quantity=100,
        quality_grade="Export",
        origin="Ratnagiri",
        base_market_price=200000,
        attributes={"ripeness": "optimal", "export_grade": True}
    )
    
    # Set budget and seller minimum
    buyer_budget = 190000  # Tight budget scenario
    seller_min = 160000    # Seller's cost
    
    # Create agents
    buyer = YourBuyerAgent("CharmingBuyer")
    seller = AdvancedSellerAgent(seller_min, seller_strategy)
    
    # Start conversation
    conversation_manager = ConversationManager(buyer, seller, product, buyer_budget)
    conversation_history = conversation_manager.start_conversation()
    
    return conversation_manager, conversation_history

def run_multiple_scenarios():
    """Run multiple conversation scenarios"""
    scenarios = [
        ("seductive", "balanced", "Balanced Seller vs Seductive Buyer"),
        ("seductive", "aggressive", "Aggressive Seller vs Seductive Buyer"),
        ("seductive", "conservative", "Conservative Seller vs Seductive Buyer")
    ]
    
    results = []
    
    for buyer_strat, seller_strat, description in scenarios:
        print(f"\n{'#'*80}")
        print(f"SCENARIO: {description}")
        print(f"{'#'*80}")
        
        manager, history = run_full_conversation(buyer_strat, seller_strat)
        
        results.append({
            "scenario": description,
            "deal_made": manager.deal_status == DealStatus.ACCEPTED,
            "final_price": manager.final_price,
            "rounds": manager.round_number,
            "conversation": history
        })
    
    # Summary report
    print(f"\n{'='*80}")
    print("SCENARIO SUMMARY")
    print(f"{'='*80}")
    
    for result in results:
        status = "✅ DEAL" if result["deal_made"] else "❌ NO DEAL"
        price_info = f"at ₹{result['final_price']:,}" if result["final_price"] else ""
        print(f"{status:15} | {result['scenario']:40} | Round {result['rounds']} {price_info}")

# ============================================
# CONVERSATION EXPORT UTILITIES
# ============================================

def export_conversation_to_json(conversation_history: List[ConversationTurn], filename: str):
    """Export conversation to JSON for analysis"""
    conversation_data = []
    for turn in conversation_history:
        conversation_data.append({
            "speaker": turn.speaker,
            "message": turn.message,
            "price_offer": turn.price_offer,
            "round_number": turn.round_number,
            "deal_status": turn.deal_status.value
        })
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(conversation_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Conversation exported to {filename}")

def print_conversation_transcript(conversation_history: List[ConversationTurn]):
    """Print a clean transcript of the conversation"""
    print(f"\n{'='*80}")
    print("CONVERSATION TRANSCRIPT")
    print(f"{'='*80}")
    
    for turn in conversation_history:
        if turn.speaker == "system":
            print(f"\n[SYSTEM] {turn.message}")
        else:
            speaker_name = "BUYER" if turn.speaker == "buyer" else "SELLER"
            price_info = f" (₹{turn.price_offer:,})" if turn.price_offer else ""
            print(f"\n[{speaker_name}]{price_info}: {turn.message}")
    
    print(f"\n{'='*80}\n")

# ============================================
# INTERACTIVE CONVERSATION MODE
# ============================================

class InteractiveNegotiation:
    """Allow human to negotiate against an AI agent"""
    
    def __init__(self, ai_agent, product: Product, human_budget: int):
        self.ai_agent = ai_agent
        self.product = product
        self.human_budget = human_budget
        self.conversation_history = []
        self.round_number = 0
        self.human_offers = []
        self.ai_offers = []
        
    def start_interactive_session(self):
        """Start an interactive negotiation session"""
        print(f"\n{'='*60}")
        print(f"INTERACTIVE NEGOTIATION")
        print(f"You are negotiating to BUY: {self.product.name}")
        print(f"Quality: {self.product.quality_grade} | Quantity: {self.product.quantity}")
        print(f"Market Price: ₹{self.product.base_market_price:,}")
        print(f"Your Budget: ₹{self.human_budget:,}")
        print(f"{'='*60}")
        
        # AI opens
        ai_price, ai_message = self.ai_agent.get_opening_price(self.product)
        print(f"\n[AI SELLER] (₹{ai_price:,}): {ai_message}")
        self.ai_offers.append(ai_price)
        
        # Human negotiation loop
        while self.round_number < 10:
            self.round_number += 1
            
            # Get human response
            print(f"\n--- Round {self.round_number} ---")
            human_input = input("Your response (or 'quit' to exit): ").strip()
            
            if human_input.lower() in ['quit', 'exit', 'q']:
                print("Negotiation ended by user.")
                break
            
            # Extract price from human input
            human_price = self._extract_price_from_input(human_input)
            if human_price is None:
                print("Please include a price offer in your message (e.g., '₹150000')")
                continue
            
            if human_price > self.human_budget:
                print(f"That exceeds your budget of ₹{self.human_budget:,}! Try again.")
                continue
            
            self.human_offers.append(human_price)
            print(f"[YOU] (₹{human_price:,}): {human_input}")
            
            # AI responds
            ai_counter, ai_response, ai_accepts = self.ai_agent.respond_to_buyer(human_price, self.round_number)
            
            if ai_accepts:
                print(f"\n[AI SELLER] ACCEPTS: {ai_response}")
                print(f"\n🎉 DEAL CLOSED at ₹{human_price:,}!")
                print(f"You saved ₹{self.human_budget - human_price:,} from your budget!")
                break
            else:
                print(f"\n[AI SELLER] (₹{ai_counter:,}): {ai_response}")
                self.ai_offers.append(ai_counter)
        
        if self.round_number >= 10:
            print("\n⏰ Negotiation timed out!")
    
    def _extract_price_from_input(self, text: str) -> Optional[int]:
        """Extract price from human input"""
        # Look for ₹123,456 or plain numbers
        price_patterns = [
            r"₹\s*([\d,]+)",
            r"(\d{4,})",  # 4+ digit numbers
            r"(\d+,\d+)",  # comma-separated numbers
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1).replace(",", ""))
        return None

# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    print("🤖 AI NEGOTIATION CONVERSATION SYSTEM")
    print("=====================================")
    
    choice = input("\nChoose mode:\n1. Auto conversation (AI vs AI)\n2. Interactive mode (You vs AI)\n3. Multiple scenarios\n\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🔄 Running automatic AI vs AI conversation...")
        manager, history = run_full_conversation()
        print_conversation_transcript(history)
        
        # Option to export
        export_choice = input("\nExport conversation to JSON? (y/n): ").strip().lower()
        if export_choice == 'y':
            export_conversation_to_json(history, "negotiation_log.json")
    
    elif choice == "2":
        print("\n👤 Starting interactive mode...")
        product = Product(
            name="Alphonso Mangoes",
            category="Mangoes", 
            quantity=100,
            quality_grade="A",
            origin="Ratnagiri",
            base_market_price=180000,
            attributes={"ripeness": "optimal", "export_grade": True}
        )
        
        human_budget = 170000
        seller_min = 140000
        
        ai_seller = AdvancedSellerAgent(seller_min, "balanced")
        interactive_session = InteractiveNegotiation(ai_seller, product, human_budget)
        interactive_session.start_interactive_session()
    
    elif choice == "3":
        print("\n📊 Running multiple scenarios...")
        run_multiple_scenarios()
    
    else:
        print("Invalid choice. Running default auto conversation...")
        manager, history = run_full_conversation()
        print_conversation_transcript(history)

# ============================================
# ADVANCED CONVERSATION FEATURES
# ============================================

class ConversationAnalyzer:
    """Analyze conversation patterns and effectiveness"""
    
    @staticmethod
    def analyze_conversation(conversation_history: List[ConversationTurn]) -> Dict[str, Any]:
        """Comprehensive analysis of the negotiation conversation"""
        
        buyer_turns = [t for t in conversation_history if t.speaker == "buyer"]
        seller_turns = [t for t in conversation_history if t.speaker == "seller"]
        
        buyer_prices = [t.price_offer for t in buyer_turns if t.price_offer]
        seller_prices = [t.price_offer for t in seller_turns if t.price_offer]
        
        analysis = {
            "total_rounds": len([t for t in conversation_history if t.speaker != "system"]) // 2,
            "deal_outcome": conversation_history[-1].deal_status.value if conversation_history else "unknown",
            "price_movements": {
                "buyer_opening": buyer_prices[0] if buyer_prices else None,
                "buyer_final": buyer_prices[-1] if buyer_prices else None,
                "seller_opening": seller_prices[0] if seller_prices else None,
                "seller_final": seller_prices[-1] if seller_prices else None,
                "convergence_rate": ConversationAnalyzer._calculate_convergence(buyer_prices, seller_prices)
            },
            "communication_patterns": {
                "avg_buyer_msg_length": sum(len(t.message.split()) for t in buyer_turns) / len(buyer_turns) if buyer_turns else 0,
                "avg_seller_msg_length": sum(len(t.message.split()) for t in seller_turns) / len(seller_turns) if seller_turns else 0,
                "buyer_sentiment": ConversationAnalyzer._analyze_sentiment(buyer_turns),
                "seller_sentiment": ConversationAnalyzer._analyze_sentiment(seller_turns)
            }
        }
        
        return analysis
    
    @staticmethod
    def _calculate_convergence(buyer_prices: List[int], seller_prices: List[int]) -> float:
        """Calculate how quickly prices converged"""
        if len(buyer_prices) < 2 or len(seller_prices) < 2:
            return 0.0
        
        initial_gap = abs(seller_prices[0] - buyer_prices[0])
        final_gap = abs(seller_prices[-1] - buyer_prices[-1])
        
        if initial_gap == 0:
            return 1.0
        
        convergence = 1 - (final_gap / initial_gap)
        return max(0.0, min(1.0, convergence))
    
    @staticmethod
    def _analyze_sentiment(turns: List[ConversationTurn]) -> str:
        """Basic sentiment analysis of conversation turns"""
        positive_words = ["excellent", "wonderful", "great", "pleased", "delighted", "perfect", "fantastic"]
        negative_words = ["difficult", "tough", "hard", "impossible", "unfair", "unreasonable"]
        
        total_positive = sum(sum(1 for word in positive_words if word in turn.message.lower()) for turn in turns)
        total_negative = sum(sum(1 for word in negative_words if word in turn.message.lower()) for turn in turns)
        
        if total_positive > total_negative:
            return "positive"
        elif total_negative > total_positive:
            return "negative"
        else:
            return "neutral"

class ConversationLogger:
    """Advanced logging and tracking of negotiations"""
    
    def __init__(self):
        self.session_logs = []
    
    def log_session(self, conversation_manager: ConversationManager, conversation_history: List[ConversationTurn]):
        """Log a complete negotiation session"""
        analysis = ConversationAnalyzer.analyze_conversation(conversation_history)
        
        session_data = {
            "timestamp": f"Session_{len(self.session_logs) + 1}",
            "product": {
                "name": conversation_manager.product.name,
                "quality": conversation_manager.product.quality_grade,
                "quantity": conversation_manager.product.quantity,
                "market_price": conversation_manager.product.base_market_price
            },
            "negotiation_setup": {
                "buyer_budget": conversation_manager.buyer_budget,
                "buyer_agent": conversation_manager.buyer_agent.name,
                "seller_strategy": getattr(conversation_manager.seller_agent, 'strategy', 'unknown')
            },
            "results": {
                "deal_status": conversation_manager.deal_status.value,
                "final_price": conversation_manager.final_price,
                "rounds_completed": conversation_manager.round_number,
                "buyer_savings": conversation_manager.buyer_budget - conversation_manager.final_price if conversation_manager.final_price else 0
            },
            "analysis": analysis,
            "conversation": [
                {
                    "speaker": turn.speaker,
                    "message": turn.message,
                    "price": turn.price_offer,
                    "round": turn.round_number
                }
                for turn in conversation_history
            ]
        }
        
        self.session_logs.append(session_data)
    
    def print_session_summary(self):
        """Print summary of all logged sessions"""
        if not self.session_logs:
            print("No sessions logged yet.")
            return
        
        print(f"\n{'='*80}")
        print(f"SESSION SUMMARY ({len(self.session_logs)} sessions)")
        print(f"{'='*80}")
        
        successful_deals = [s for s in self.session_logs if s["results"]["deal_status"] == "accepted"]
        success_rate = len(successful_deals) / len(self.session_logs) * 100
        
        print(f"Success Rate: {success_rate:.1f}% ({len(successful_deals)}/{len(self.session_logs)})")
        
        if successful_deals:
            avg_savings = sum(s["results"]["buyer_savings"] for s in successful_deals) / len(successful_deals)
            avg_rounds = sum(s["results"]["rounds_completed"] for s in successful_deals) / len(successful_deals)
            print(f"Average Savings: ₹{avg_savings:,.0f}")
            print(f"Average Rounds: {avg_rounds:.1f}")
        
        print(f"\nDetailed Results:")
        for i, session in enumerate(self.session_logs, 1):
            status_icon = "✅" if session["results"]["deal_status"] == "accepted" else "❌"
            product_info = f"{session['product']['name']} ({session['product']['quality']})"
            price_info = f"₹{session['results']['final_price']:,}" if session['results']['final_price'] else "No deal"
            print(f"{i:2d}. {status_icon} {product_info:30} | {price_info:15} | Round {session['results']['rounds_completed']}")

# ============================================
# CONVERSATION TEMPLATES
# ============================================

def create_conversation_scenario(product_name: str, quality: str, scenario_difficulty: str) -> Tuple[Product, int, int]:
    """Create predefined conversation scenarios"""
    
    products_db = {
        "alphonso_mangoes": Product("Alphonso Mangoes", "Mangoes", 100, quality, "Ratnagiri", 180000, {"export_grade": True}),
        "kesar_mangoes": Product("Kesar Mangoes", "Mangoes", 150, quality, "Gujarat", 150000, {"export_grade": False}),
        "basmati_rice": Product("Basmati Rice", "Rice", 200, quality, "Punjab", 120000, {"aging": "12_months"}),
        "black_pepper": Product("Black Pepper", "Spices", 50, quality, "Kerala", 250000, {"moisture_content": "10%"}),
        "cashews": Product("Cashews", "Nuts", 75, quality, "Karnataka", 300000, {"size_grade": "W240"})
    }
    
    product = products_db.get(product_name.lower().replace(" ", "_"))
    if not product:
        # Default product
        product = products_db["alphonso_mangoes"]
    
    # Adjust scenario difficulty
    if scenario_difficulty == "easy":
        buyer_budget = int(product.base_market_price * 1.3)
        seller_min = int(product.base_market_price * 0.75)
    elif scenario_difficulty == "medium":
        buyer_budget = int(product.base_market_price * 1.1)
        seller_min = int(product.base_market_price * 0.85)
    elif scenario_difficulty == "hard":
        buyer_budget = int(product.base_market_price * 0.95)
        seller_min = int(product.base_market_price * 0.88)
    else:  # custom
        buyer_budget = int(product.base_market_price * 1.0)
        seller_min = int(product.base_market_price * 0.80)
    
    return product, buyer_budget, seller_min

def demo_conversation_showcase():
    """Showcase different conversation styles and outcomes"""
    print(f"\n{'🎭'*20}")
    print("CONVERSATION SHOWCASE")
    print(f"{'🎭'*20}")
    
    logger = ConversationLogger()
    
    # Showcase different products and difficulties
    scenarios = [
        ("Alphonso Mangoes", "Export", "medium"),
        ("Basmati Rice", "A", "easy"),
        ("Black Pepper", "B", "hard"),
        ("Cashews", "Export", "medium")
    ]
    
    for product_name, quality, difficulty in scenarios:
        print(f"\n{'🔹'*40}")
        print(f"SHOWCASE: {product_name} ({quality} grade, {difficulty} scenario)")
        print(f"{'🔹'*40}")
        
        product, buyer_budget, seller_min = create_conversation_scenario(product_name, quality, difficulty)
        
        buyer = YourBuyerAgent("SeductiveBuyer")
        seller = AdvancedSellerAgent(seller_min, "balanced")
        
        manager = ConversationManager(buyer, seller, product, buyer_budget)
        history = manager.start_conversation()
        
        logger.log_session(manager, history)
    
    # Print comprehensive summary
    logger.print_session_summary()

# ============================================
# USAGE EXAMPLES
# ============================================

def example_usage():
    """Show how to use the conversation system"""
    
    print("""
USAGE EXAMPLES:
===============

1. Run a single AI vs AI conversation:
   manager, history = run_full_conversation()
   print_conversation_transcript(history)

2. Start interactive mode (human vs AI):
   product = Product(...)
   ai_seller = AdvancedSellerAgent(min_price, "aggressive")
   session = InteractiveNegotiation(ai_seller, product, your_budget)
   session.start_interactive_session()

3. Run multiple scenarios with analysis:
   run_multiple_scenarios()

4. Create custom scenarios:
   product, budget, seller_min = create_conversation_scenario("Alphonso Mangoes", "Export", "hard")

5. Full showcase with logging:
   demo_conversation_showcase()
""")

# Run the conversation system
if __name__ == "__main__":
    choice = input("\nSelect option:\n1. Single conversation\n2. Interactive mode\n3. Multiple scenarios\n4. Full showcase\n5. Show usage examples\n\nChoice (1-5): ").strip()
    
    if choice == "1":
        manager, history = run_full_conversation()
        print_conversation_transcript(history)
    elif choice == "2":
        product = Product("Alphonso Mangoes", "Mangoes", 100, "A", "Ratnagiri", 180000, {"export_grade": True})
        ai_seller = AdvancedSellerAgent(140000, "balanced")
        session = InteractiveNegotiation(ai_seller, product, 170000)
        session.start_interactive_session()
    elif choice == "3":
        run_multiple_scenarios()
    elif choice == "4":
        demo_conversation_showcase()
    elif choice == "5":
        example_usage()
    else:
        print("Running default showcase...")
        demo_conversation_showcase()