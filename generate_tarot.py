#!/usr/bin/env python3
"""Generate a complete Rider-Waite-Smith tarot deck JSON file."""

import json

major_arcana = [
    {
        "id": 0,
        "name": "The Fool",
        "suit": "major",
        "keywords": ["beginnings", "innocence", "spontaneity", "leap of faith"],
        "upright": "New beginnings, fresh start, taking a leap of faith. Trust the journey even when the path is unclear.",
        "daily": "The universe is asking you to trust and take that first step. You are more ready than you feel."
    },
    {
        "id": 1,
        "name": "The Magician",
        "suit": "major",
        "keywords": ["willpower", "skill", "resourcefulness", "manifestation"],
        "upright": "You have all the tools you need to succeed. Channel your will and focus to manifest your desires into reality.",
        "daily": "Your power to create is at its peak today — use your talents and resources to make something happen."
    },
    {
        "id": 2,
        "name": "The High Priestess",
        "suit": "major",
        "keywords": ["intuition", "mystery", "subconscious", "inner knowledge"],
        "upright": "Trust your inner voice and the wisdom that arises from stillness. The answers you seek lie within, not outside yourself.",
        "daily": "Pause and listen to your intuition — the quiet voice within knows the way forward."
    },
    {
        "id": 3,
        "name": "The Empress",
        "suit": "major",
        "keywords": ["abundance", "nurturing", "fertility", "nature"],
        "upright": "Abundance, fertility, and creative growth surround you. Nurture yourself and others with compassion and generosity.",
        "daily": "Allow yourself to receive the abundance flowing toward you — you deserve to be nurtured."
    },
    {
        "id": 4,
        "name": "The Emperor",
        "suit": "major",
        "keywords": ["authority", "structure", "stability", "protection"],
        "upright": "Establish order and take command of your domain. Strong foundations are built through discipline, structure, and responsible leadership.",
        "daily": "Step into your authority today — the structure you build now will support you for a long time."
    },
    {
        "id": 5,
        "name": "The Hierophant",
        "suit": "major",
        "keywords": ["tradition", "spiritual guidance", "conformity", "wisdom"],
        "upright": "Seek wisdom from established traditions, mentors, or spiritual teachers. There is value in time-tested knowledge and shared beliefs.",
        "daily": "A wise teacher or a sacred tradition has something important to offer you today."
    },
    {
        "id": 6,
        "name": "The Lovers",
        "suit": "major",
        "keywords": ["love", "harmony", "choices", "union"],
        "upright": "A significant choice rooted in love and values presents itself. Follow your heart while honoring what truly matters to you.",
        "daily": "A choice about love or values is calling — let your heart speak honestly."
    },
    {
        "id": 7,
        "name": "The Chariot",
        "suit": "major",
        "keywords": ["willpower", "determination", "victory", "confidence"],
        "upright": "Harness opposing forces within yourself to charge forward with confidence. Victory comes through focus and sheer determination.",
        "daily": "You have the strength to overcome any obstacle today — stay focused and drive forward."
    },
    {
        "id": 8,
        "name": "Strength",
        "suit": "major",
        "keywords": ["courage", "inner strength", "compassion", "patience"],
        "upright": "True strength is gentle, patient, and rooted in compassion. Face challenges with courage and quiet confidence rather than aggression.",
        "daily": "Your inner courage is greater than you know — meet today's challenges with a calm and steady heart."
    },
    {
        "id": 9,
        "name": "The Hermit",
        "suit": "major",
        "keywords": ["solitude", "introspection", "wisdom", "guidance"],
        "upright": "Withdraw from the noise of the world to seek inner truth. Solitude and quiet reflection will illuminate your path forward.",
        "daily": "Some answers can only be found in stillness — take time alone to listen to your inner guide."
    },
    {
        "id": 10,
        "name": "Wheel of Fortune",
        "suit": "major",
        "keywords": ["change", "cycles", "destiny", "turning point"],
        "upright": "Life is in constant motion — a turning point is here. Embrace the cycle of change and know that luck and fate are shifting in your favor.",
        "daily": "Change is coming, and it brings opportunity — trust the turning of the wheel."
    },
    {
        "id": 11,
        "name": "Justice",
        "suit": "major",
        "keywords": ["fairness", "truth", "accountability", "balance"],
        "upright": "Truth and fairness prevail. Your actions have consequences — be honest, take responsibility, and trust that balance will be restored.",
        "daily": "The truth will come to light today — act with integrity and fairness in all you do."
    },
    {
        "id": 12,
        "name": "The Hanged Man",
        "suit": "major",
        "keywords": ["surrender", "new perspective", "pause", "sacrifice"],
        "upright": "Release the need to control and see the world from a new angle. Sometimes the best action is to pause, surrender, and wait.",
        "daily": "Stop struggling and look at the situation from a completely different angle — the answer is in the shift."
    },
    {
        "id": 13,
        "name": "Death",
        "suit": "major",
        "keywords": ["transformation", "endings", "rebirth", "release"],
        "upright": "An ending clears the way for profound transformation. Release what no longer serves you so something new can be born.",
        "daily": "An ending is not a loss — it is the clearing of ground for something new to grow."
    },
    {
        "id": 14,
        "name": "Temperance",
        "suit": "major",
        "keywords": ["balance", "moderation", "patience", "harmony"],
        "upright": "Find the middle path through patience, moderation, and blending opposites. Balance brings peace and sustainable progress.",
        "daily": "Slow down, find the middle way, and let patience bring harmony to your day."
    },
    {
        "id": 15,
        "name": "The Devil",
        "suit": "major",
        "keywords": ["bondage", "materialism", "shadow self", "addiction"],
        "upright": "You may feel trapped by material desires, unhealthy patterns, or limiting beliefs. Recognize the chains to break free.",
        "daily": "What is holding you back? Name the chain, and you take the first step to breaking it."
    },
    {
        "id": 16,
        "name": "The Tower",
        "suit": "major",
        "keywords": ["upheaval", "sudden change", "revelation", "destruction"],
        "upright": "A sudden, disruptive revelation shatters old structures. It feels chaotic, but the destruction clears the way for a truer foundation.",
        "daily": "What falls apart today makes room for something far more authentic to be built."
    },
    {
        "id": 17,
        "name": "The Star",
        "suit": "major",
        "keywords": ["hope", "inspiration", "renewal", "serenity"],
        "upright": "After hardship, hope and inspiration return. Trust the universe, heal your spirit, and let your inner light guide you forward.",
        "daily": "Hope is your compass today — trust that the universe is guiding you toward healing and peace."
    },
    {
        "id": 18,
        "name": "The Moon",
        "suit": "major",
        "keywords": ["illusion", "fear", "intuition", "the unknown"],
        "upright": "Things are not as they seem. Fear and illusion cloud your vision — rely on your intuition to navigate uncertainty and hidden truths.",
        "daily": "Not everything is as it appears today — look beneath the surface and trust your instincts."
    },
    {
        "id": 19,
        "name": "The Sun",
        "suit": "major",
        "keywords": ["joy", "success", "vitality", "celebration"],
        "upright": "Radiant joy, success, and clarity fill your world. Celebrate your achievements and bask in the warmth of a bright, positive future.",
        "daily": "Today is a day of warmth and clarity — let your light shine and celebrate life."
    },
    {
        "id": 20,
        "name": "Judgement",
        "suit": "major",
        "keywords": ["rebirth", "inner calling", "absolution", "awakening"],
        "upright": "A profound inner calling awakens you to a new phase of life. Rise to your higher purpose and answer the summons of your soul.",
        "daily": "You are being called to rise — listen to the deep longing in your soul and answer it."
    },
    {
        "id": 21,
        "name": "The World",
        "suit": "major",
        "keywords": ["completion", "fulfillment", "wholeness", "accomplishment"],
        "upright": "A major cycle reaches its successful conclusion. You have achieved integration, fulfillment, and a deep sense of completeness.",
        "daily": "A cycle closes and you stand complete — celebrate how far you have come."
    }
]

# --- MINOR ARCANA ---

wands = [
    {
        "id": 1,
        "name": "Ace of Wands",
        "suit": "wands",
        "keywords": ["inspiration", "new beginning", "creative spark", "potential"],
        "upright": "A burst of creative energy and inspiration ignites a new venture. Seize the spark of passion and take bold action.",
        "daily": "A creative spark is ready to ignite — grab this inspiration and run with it."
    },
    {
        "id": 2,
        "name": "Two of Wands",
        "suit": "wands",
        "keywords": ["planning", "future vision", "decision", "discovery"],
        "upright": "You stand at a crossroads with the world before you. Make plans, dream big, and step beyond your comfort zone into greater possibilities.",
        "daily": "Look ahead and plan your next move — the world is waiting for you to step into it."
    },
    {
        "id": 3,
        "name": "Three of Wands",
        "suit": "wands",
        "keywords": ["expansion", "progress", "foresight", "exploration"],
        "upright": "Your plans are gaining momentum and opportunities are expanding. Look ahead with confidence and prepare for the next stage of growth.",
        "daily": "Your horizon is widening — the progress you've made is opening doors you couldn't see before."
    },
    {
        "id": 4,
        "name": "Four of Wands",
        "suit": "wands",
        "keywords": ["celebration", "harmony", "homecoming", "community"],
        "upright": "A time of joy, celebration, and harmony in your home or community. Rejoice in the stability and happiness you have built together.",
        "daily": "Celebrate the foundation you've built — gather with loved ones and enjoy this moment of harmony."
    },
    {
        "id": 5,
        "name": "Five of Wands",
        "suit": "wands",
        "keywords": ["competition", "conflict", "tension", "diversity"],
        "upright": "Competition, clashing egos, and spirited disagreement create tension. Channel this friction into productive growth rather than destructive conflict.",
        "daily": "You may face opposition today — meet it as a challenge to grow stronger, not a threat."
    },
    {
        "id": 6,
        "name": "Six of Wands",
        "suit": "wands",
        "keywords": ["victory", "recognition", "public acclaim", "confidence"],
        "upright": "You are being recognized for your achievements. Bask in the well-earned praise and let this victory boost your confidence.",
        "daily": "Your efforts are being noticed — accept the praise and let this success fuel your momentum."
    },
    {
        "id": 7,
        "name": "Seven of Wands",
        "suit": "wands",
        "keywords": ["defense", "perseverance", "standing your ground", "challenge"],
        "upright": "You are being challenged and must defend your position. Stand your ground with courage and hold fast to what you have earned.",
        "daily": "Stand firm — people may test your position, but you have the strength to hold your ground."
    },
    {
        "id": 8,
        "name": "Eight of Wands",
        "suit": "wands",
        "keywords": ["speed", "action", "momentum", "progress"],
        "upright": "Things are moving quickly — messages, travel, and rapid progress are on the horizon. Ride the wave of momentum and act swiftly.",
        "daily": "Everything is accelerating — stay alert and ride the wave of rapid progress."
    },
    {
        "id": 9,
        "name": "Nine of Wands",
        "suit": "wands",
        "keywords": ["resilience", "persistence", "boundaries", "last stand"],
        "upright": "You are weary from the battle but must hold the line one last time. Draw on your resilience — the final challenge is almost over.",
        "daily": "You are tired but almost there — one final push and the struggle will be behind you."
    },
    {
        "id": 10,
        "name": "Ten of Wands",
        "suit": "wands",
        "keywords": ["burden", "responsibility", "overwork", "endurance"],
        "upright": "You are carrying too much weight and feeling overwhelmed. Delegate, set priorities, and release what is not yours to carry alone.",
        "daily": "The burden is heavy today — ask for help or put something down before you break."
    },
    {
        "id": 11,
        "name": "Page of Wands",
        "suit": "wands",
        "keywords": ["enthusiasm", "exploration", "adventure", "free spirit"],
        "upright": "A youthful, adventurous energy invites you to explore something new. Follow your curiosity with enthusiasm and an open heart.",
        "daily": "Say yes to your curiosity today — a new adventure is calling your name."
    },
    {
        "id": 12,
        "name": "Knight of Wands",
        "suit": "wands",
        "keywords": ["passion", "action", "adventure", "impulsiveness"],
        "upright": "A burst of fiery energy propels you toward your goal with passion and courage. Act boldly, but watch for impulsiveness.",
        "daily": "Charge forward with passion today — but take a breath before you leap."
    },
    {
        "id": 13,
        "name": "Queen of Wands",
        "suit": "wands",
        "keywords": ["confidence", "warmth", "determination", "charisma"],
        "upright": "Radiant confidence, warmth, and fierce determination define this energy. Lead with charisma and inspire others with your vitality.",
        "daily": "Own your power with warmth and confidence today — your magnetism draws people to you."
    },
    {
        "id": 14,
        "name": "King of Wands",
        "suit": "wands",
        "keywords": ["vision", "leadership", "entrepreneurship", "honor"],
        "upright": "A visionary leader who takes bold, honorable action. Command respect by combining big-picture vision with decisive, inspired leadership.",
        "daily": "Step into bold leadership today — your vision and courage inspire others to follow."
    }
]

cups = [
    {
        "id": 1,
        "name": "Ace of Cups",
        "suit": "cups",
        "keywords": ["love", "new feeling", "compassion", "emotional awakening"],
        "upright": "An outpouring of love, joy, and emotional fulfillment. A new relationship or deep emotional connection is being offered to you.",
        "daily": "Your heart is opening — welcome the love and emotional richness flowing toward you."
    },
    {
        "id": 2,
        "name": "Two of Cups",
        "suit": "cups",
        "keywords": ["partnership", "unity", "attraction", "mutual love"],
        "upright": "A deep emotional bond forms between two people. This card celebrates love, friendship, partnership, and mutual respect.",
        "daily": "A beautiful connection is in the air today — cherish the harmony between two hearts."
    },
    {
        "id": 3,
        "name": "Three of Cups",
        "suit": "cups",
        "keywords": ["friendship", "celebration", "community", "joy"],
        "upright": "A time of joyful gathering with friends and community. Celebrate togetherness, share happiness, and toast to life's blessings.",
        "daily": "Gather with people who lift your spirits — joy multiplies when it is shared."
    },
    {
        "id": 4,
        "name": "Four of Cups",
        "suit": "cups",
        "keywords": ["apathy", "contemplation", "discontent", "restlessness"],
        "upright": "A sense of dissatisfaction or apathy settles in. You may be overlooking a genuine opportunity because you are focused on what you lack.",
        "daily": "Look up from your discontent — an unexpected offer is right in front of you, but you might miss it."
    },
    {
        "id": 5,
        "name": "Five of Cups",
        "suit": "cups",
        "keywords": ["loss", "grief", "regret", "disappointment"],
        "upright": "Focusing on what has been lost prevents you from seeing what still remains. Grieve, then turn to find the two cups still standing.",
        "daily": "Turn away from what is spilled and see what still stands — there is more left than you think."
    },
    {
        "id": 6,
        "name": "Six of Cups",
        "suit": "cups",
        "keywords": ["nostalgia", "childhood", "innocence", "reunion"],
        "upright": "A wave of nostalgia brings memories of simpler, happier times. Reconnect with your inner child or someone from your past.",
        "daily": "A sweet memory or a familiar face from the past brings warmth to your heart today."
    },
    {
        "id": 7,
        "name": "Seven of Cups",
        "suit": "cups",
        "keywords": ["illusion", "fantasy", "choices", "wishful thinking"],
        "upright": "Many tempting options appear, but not all are what they seem. Dream big, but ground your choices in reality to avoid illusion.",
        "daily": "You have many options, but not all are real — keep your feet on the ground as you dream."
    },
    {
        "id": 8,
        "name": "Eight of Cups",
        "suit": "cups",
        "keywords": ["departure", "letting go", "search for truth", "walking away"],
        "upright": "The courage to walk away from what no longer fulfills you. A journey toward deeper meaning and emotional truth begins now.",
        "daily": "It is time to leave behind what no longer serves your soul — a deeper truth calls you onward."
    },
    {
        "id": 9,
        "name": "Nine of Cups",
        "suit": "cups",
        "keywords": ["satisfaction", "wishes fulfilled", "contentment", "indulgence"],
        "upright": "Your wishes are coming true. A moment of deep satisfaction, emotional fulfillment, and contentment with life's blessings.",
        "daily": "Your heart's desire is within reach — enjoy the deep satisfaction of a wish fulfilled."
    },
    {
        "id": 10,
        "name": "Ten of Cups",
        "suit": "cups",
        "keywords": ["happiness", "family", "emotional fulfillment", "bliss"],
        "upright": "Emotional fulfillment and lasting happiness in home and family. The dream of a harmonious, loving life is realized.",
        "daily": "Your heart is full — today brings a glimpse of the deep happiness you deserve."
    },
    {
        "id": 11,
        "name": "Page of Cups",
        "suit": "cups",
        "keywords": ["intuition", "curiosity", "creativity", "emotional messages"],
        "upright": "A message of love or an intuitive nudge arrives. Approach life with the open-hearted curiosity of a dreamer and artist.",
        "daily": "A creative or intuitive message is coming through — stay curious and open-hearted."
    },
    {
        "id": 12,
        "name": "Knight of Cups",
        "suit": "cups",
        "keywords": ["romance", "charm", "imagination", "pursuit of beauty"],
        "upright": "A romantic, charming energy pursues the heart's deepest desires. Follow your dreams, but keep one foot in reality.",
        "daily": "Follow your heart's desire today — let beauty, romance, and imagination guide you."
    },
    {
        "id": 13,
        "name": "Queen of Cups",
        "suit": "cups",
        "keywords": ["compassion", "emotional depth", "intuition", "nurturing"],
        "upright": "Deep emotional wisdom flows through you. Nurture others with compassion while honoring your own emotional boundaries.",
        "daily": "Lead with your heart today — your compassion and intuition are your greatest strengths."
    },
    {
        "id": 14,
        "name": "King of Cups",
        "suit": "cups",
        "keywords": ["emotional balance", "wisdom", "calm", "diplomacy"],
        "upright": "Mastery of the emotional realm through calm wisdom and compassion. You lead with a balanced heart and steady, diplomatic presence.",
        "daily": "Stay calm and steady — your emotional maturity is the anchor those around you need."
    }
]

swords = [
    {
        "id": 1,
        "name": "Ace of Swords",
        "suit": "swords",
        "keywords": ["clarity", "truth", "breakthrough", "new idea"],
        "upright": "A moment of piercing clarity and truth cuts through confusion. A breakthrough idea or powerful new perspective emerges.",
        "daily": "A flash of clarity cuts through the fog — the truth is sharp and liberating today."
    },
    {
        "id": 2,
        "name": "Two of Swords",
        "suit": "swords",
        "keywords": ["difficult choice", "stalemate", "denial", "blocked emotions"],
        "upright": "You are at an impasse, avoiding a difficult decision. Remove the blindfold, face the truth, and choose from a place of clarity.",
        "daily": "You cannot avoid the decision forever — take off the blindfold and face what is real."
    },
    {
        "id": 3,
        "name": "Three of Swords",
        "suit": "swords",
        "keywords": ["heartbreak", "grief", "sorrow", "betrayal"],
        "upright": "Painful emotions come to the surface — heartbreak, sorrow, or betrayal. The only way through is to feel, heal, and release.",
        "daily": "Heartache cannot be ignored — let yourself feel the pain so it can begin to heal."
    },
    {
        "id": 4,
        "name": "Four of Swords",
        "suit": "swords",
        "keywords": ["rest", "recuperation", "meditation", "retreat"],
        "upright": "A period of rest, reflection, and recovery is needed. Step back from the battle to restore your mind and spirit.",
        "daily": "Give yourself permission to rest — stillness is not weakness, it is wisdom."
    },
    {
        "id": 5,
        "name": "Five of Swords",
        "suit": "swords",
        "keywords": ["conflict", "defeat", "loss", "unfair victory"],
        "upright": "A hollow victory leaves a bitter taste. Winning at the expense of others creates isolation — choose your battles wisely.",
        "daily": "Winning this fight might cost you more than losing would — is the battle worth it?"
    },
    {
        "id": 6,
        "name": "Six of Swords",
        "suit": "swords",
        "keywords": ["transition", "moving on", "letting go", "journey"],
        "upright": "A difficult but necessary transition carries you toward calmer waters. You are leaving turmoil behind, even if the journey is bittersweet.",
        "daily": "You are moving toward calmer waters — let go of the past and trust the journey."
    },
    {
        "id": 7,
        "name": "Seven of Swords",
        "suit": "swords",
        "keywords": ["deception", "strategy", "stealth", "betrayal"],
        "upright": "Someone may be acting dishonestly, or you need a strategic retreat. Be clever, but ensure your actions align with your integrity.",
        "daily": "Watch for hidden motives today — and be strategic rather than confrontational."
    },
    {
        "id": 8,
        "name": "Eight of Swords",
        "suit": "swords",
        "keywords": ["restriction", "self-imposed limitation", "fear", "negative thinking"],
        "upright": "You feel trapped, but the cage is largely of your own making. Challenge the fearful thoughts that bind you — you are freer than you believe.",
        "daily": "The prison is in your mind — question every thought that tells you that you cannot escape."
    },
    {
        "id": 9,
        "name": "Nine of Swords",
        "suit": "swords",
        "keywords": ["anxiety", "worry", "nightmares", "fear"],
        "upright": "Overwhelming anxiety and worry keep you up at night. Your fears are magnified by your mind — reach out for support and perspective.",
        "daily": "Your worries are louder than they deserve — reach out to someone you trust for perspective."
    },
    {
        "id": 10,
        "name": "Ten of Swords",
        "suit": "swords",
        "keywords": ["rock bottom", "painful ending", "betrayal", "release"],
        "upright": "A painful chapter reaches its bitter end. It feels devastating, but the worst is over — only healing and renewal remain.",
        "daily": "You have hit the bottom, which means the only way now is up — the worst is truly over."
    },
    {
        "id": 11,
        "name": "Page of Swords",
        "suit": "swords",
        "keywords": ["curiosity", "mental agility", "new ideas", "communication"],
        "upright": "A sharp, curious mind seeks the truth. Speak your mind, ask questions, and share your ideas with enthusiasm and intellectual courage.",
        "daily": "Stay curious and speak your truth today — your sharp mind is your best tool."
    },
    {
        "id": 12,
        "name": "Knight of Swords",
        "suit": "swords",
        "keywords": ["ambition", "speed", "assertiveness", "determination"],
        "upright": "Charging ahead with fierce determination and unwavering focus. Go after your goal with speed and clarity, but avoid recklessness.",
        "daily": "Go after your goal with everything you have — but make sure you look before you charge."
    },
    {
        "id": 13,
        "name": "Queen of Swords",
        "suit": "swords",
        "keywords": ["perception", "clear communication", "independence", "truth"],
        "upright": "A clear-eyed, perceptive communicator who values truth above comfort. Make decisions with logic and direct, honest communication.",
        "daily": "Use your sharp mind and clear voice today — honesty and clarity will cut through confusion."
    },
    {
        "id": 14,
        "name": "King of Swords",
        "suit": "swords",
        "keywords": ["authority", "truth", "intellectual power", "ethics"],
        "upright": "A sovereign of clear thinking and ethical truth. Lead with intellectual rigor, fairness, and the courage to speak truth to power.",
        "daily": "Speak with authority and clarity today — the truth needs your voice and your integrity."
    }
]

pentacles = [
    {
        "id": 1,
        "name": "Ace of Pentacles",
        "suit": "pentacles",
        "keywords": ["new opportunity", "prosperity", "abundance", "manifestation"],
        "upright": "A new financial opportunity or material gift arrives. Plant the seed of prosperity with practical action and grounded intention.",
        "daily": "A seed of abundance is being offered — take practical steps today to nurture it."
    },
    {
        "id": 2,
        "name": "Two of Pentacles",
        "suit": "pentacles",
        "keywords": ["balance", "adaptability", "resource management", "juggling"],
        "upright": "Juggling multiple priorities requires flexibility and balance. Stay adaptable and manage your resources wisely to keep everything in motion.",
        "daily": "Keep your balance while juggling competing demands — flexibility is your superpower today."
    },
    {
        "id": 3,
        "name": "Three of Pentacles",
        "suit": "pentacles",
        "keywords": ["teamwork", "skill building", "craftsmanship", "collaboration"],
        "upright": "Collaboration and shared expertise produce excellent work. Learn from others, contribute your skills, and build something enduring together.",
        "daily": "Your skills are needed as part of a team — collaboration will produce something greater than working alone."
    },
    {
        "id": 4,
        "name": "Four of Pentacles",
        "suit": "pentacles",
        "keywords": ["security", "conservation", "possessiveness", "control"],
        "upright": "Clinging tightly to your resources out of fear of loss. Save and protect what you have, but ask if your grip is holding you back.",
        "daily": "Hold on to what you have, but check — is your grip protecting you or keeping you from growing?"
    },
    {
        "id": 5,
        "name": "Five of Pentacles",
        "suit": "pentacles",
        "keywords": ["hardship", "poverty", "isolation", "struggle"],
        "upright": "Feeling left out in the cold — financial or emotional hardship tests your spirit. Help is available if you are willing to seek it.",
        "daily": "You may feel alone in your struggle, but help is there — you just need to reach out for it."
    },
    {
        "id": 6,
        "name": "Six of Pentacles",
        "suit": "pentacles",
        "keywords": ["generosity", "charity", "sharing", "balance of giving"],
        "upright": "A time of giving and receiving in balance. Share your abundance with others, and accept help graciously when it is offered to you.",
        "daily": "Give what you can and receive what you need — generosity flows in both directions."
    },
    {
        "id": 7,
        "name": "Seven of Pentacles",
        "suit": "pentacles",
        "keywords": ["patience", "investment", "evaluation", "long-term growth"],
        "upright": "You pause to assess the progress of your long-term efforts. Be patient — what you have planted is growing, even if it is not yet visible.",
        "daily": "Step back and evaluate your progress — patience now will be rewarded in time."
    },
    {
        "id": 8,
        "name": "Eight of Pentacles",
        "suit": "pentacles",
        "keywords": ["diligence", "craftsmanship", "skill development", "dedication"],
        "upright": "Devoted practice and attention to detail hone your craft. Hard work, discipline, and a commitment to mastery bring steady progress.",
        "daily": "Focus on the details and keep practicing — mastery comes one dedicated step at a time."
    },
    {
        "id": 9,
        "name": "Nine of Pentacles",
        "suit": "pentacles",
        "keywords": ["luxury", "self-sufficiency", "success", "refinement"],
        "upright": "You have cultivated a life of comfort and abundance through your own efforts. Enjoy the rewards of your hard-earned success and independence.",
        "daily": "Enjoy the beauty and comfort you have earned — you deserve to savor your success."
    },
    {
        "id": 10,
        "name": "Ten of Pentacles",
        "suit": "pentacles",
        "keywords": ["legacy", "wealth", "family heritage", "long-term success"],
        "upright": "A lasting legacy of abundance, family tradition, and material security. You stand on the shoulders of those who came before.",
        "daily": "Honor the legacy you are building — what you create today will benefit generations to come."
    },
    {
        "id": 11,
        "name": "Page of Pentacles",
        "suit": "pentacles",
        "keywords": ["ambition", "diligence", "learning", "new skill"],
        "upright": "A thirst for practical knowledge and a grounded, ambitious spirit. Apply yourself to learning a new skill with patience and dedication.",
        "daily": "A new skill or study is calling you — apply yourself with patience and steady effort."
    },
    {
        "id": 12,
        "name": "Knight of Pentacles",
        "suit": "pentacles",
        "keywords": ["perseverance", "responsibility", "hard work", "routine"],
        "upright": "Methodical, reliable, and dedicated to duty. Steady progress through consistent effort — you may not be fast, but you are unshakeable.",
        "daily": "Show up, do the work, stay consistent — your reliability is your greatest strength today."
    },
    {
        "id": 13,
        "name": "Queen of Pentacles",
        "suit": "pentacles",
        "keywords": ["nurturing", "practicality", "comfort", "groundedness"],
        "upright": "A warm, practical presence who creates comfort and security through grounded care. Nurture others while staying connected to the earth.",
        "daily": "Create comfort and security today — your practical care is a gift to everyone around you."
    },
    {
        "id": 14,
        "name": "King of Pentacles",
        "suit": "pentacles",
        "keywords": ["abundance", "leadership", "stability", "mastery"],
        "upright": "A master of material success who leads with generosity and grounded wisdom. You have built an empire through discipline and patience.",
        "daily": "Your wealth of wisdom and resources is a blessing — lead with generosity and steady confidence."
    }
]

deck = {
    "major_arcana": major_arcana,
    "minor_arcana": {
        "wands": wands,
        "cups": cups,
        "swords": swords,
        "pentacles": pentacles
    }
}

# Validation
total_major = len(deck["major_arcana"])
minor_suits = deck["minor_arcana"]
total_minor = sum(len(cards) for cards in minor_suits.values())
total = total_major + total_minor

print(f"Major arcana: {total_major} cards (expected 22)")
print(f"Minor arcana: {total_minor} cards (expected 56)")
print(f"Total: {total} cards (expected 78)")

assert total_major == 22, f"Expected 22 major arcana, got {total_major}"
assert total_minor == 56, f"Expected 56 minor arcana, got {total_minor}"
assert total == 78, f"Expected 78 total cards, got {total}"

# Verify all cards have required fields
for card in deck["major_arcana"]:
    for key in ["id", "name", "suit", "keywords", "upright", "daily"]:
        assert key in card, f"Missing key '{key}' in major card {card.get('name', '?')}"
    assert card["suit"] == "major", f"Major card {card['name']} has wrong suit"
    assert isinstance(card["keywords"], list) and len(card["keywords"]) >= 3, f"Need 3+ keywords for {card['name']}"

for suit_name, cards in minor_suits.items():
    for card in cards:
        for key in ["id", "name", "suit", "keywords", "upright", "daily"]:
            assert key in card, f"Missing key '{key}' in {suit_name} card {card.get('name', '?')}"
        assert card["suit"] == suit_name, f"Card {card['name']} has wrong suit, expected {suit_name}"
        assert isinstance(card["keywords"], list) and len(card["keywords"]) >= 3, f"Need 3+ keywords for {card['name']}"

# Verify IDs are sequential within major and within each suit
for i, card in enumerate(deck["major_arcana"]):
    assert card["id"] == i, f"Major card {card['name']} has id {card['id']}, expected {i}"

for suit_name, cards in minor_suits.items():
    for i, card in enumerate(cards):
        expected_id = i + 1  # Aces are 1, Kings are 14
        assert card["id"] == expected_id, f"Card {card['name']} in {suit_name} has id {card['id']}, expected {expected_id}"

print("\nAll validations passed! Writing to file...")

with open("/home/ladylefey/AstroMage/tarot_data.json", "w") as f:
    json.dump(deck, f, indent=2, ensure_ascii=False)

print("tarot_data.json written successfully.")
