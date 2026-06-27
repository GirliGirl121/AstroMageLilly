"""
astrology_knowledge.py — Simply Astrology Reference Library for MagiJournal

A comprehensive knowledge base drawing from Traditional/Hellenistic and
Medieval Islamic astrological traditions, with references to:
  - Abu Ma'shar al-Balkhi (Albumasar, 787–886 CE)
  - Al-Biruni (973–1048 CE)
  - Claudius Ptolemy (Tetrabiblos, 2nd c. CE)
  - Vettius Valens (Anthologies, 2nd c. CE)
  - Firmicus Maternus (Mathesis, 4th c. CE)
  - Ahmad al-Buni (Shams al-Ma'arif, 13th c. CE)

Each section is structured as a list of (heading, body_text) tuples for
display in the SimplyAstrologyView widget.
"""

KNOWLEDGE_SECTIONS = {
    "Zodiac Signs": [
        (
            "The Twelve Signs — Al-Buruj",
            (
                "In the Islamic tradition, the zodiac (al-buruj, 'the towers') represents the twelve stations "
                "of the Sun's annual journey. Each sign is 30° of celestial longitude and belongs to one of "
                "the four triplicities (elements): Fire, Earth, Air, Water. Signs also carry a modality — "
                "Cardinal (initiating), Fixed (sustaining), or Mutable (adapting).\n\n"
                "Al-Biruni in The Book of Instruction in the Elements of the Art of Astrology classified signs "
                "by: masculine/feminine, diurnal/nocturnal, and according to planetary rulership. Abu Ma'shar "
                "al-Balkhi in his Great Introduction further elaborated the natures of the signs through "
                "Aristotelian qualities (hot, cold, wet, dry)."
            ),
        ),
        (
            "♈ Aries — Al-Hamal (The Ram)",
            "Cardinal Fire. Ruler: Mars. Exaltation: Sun. Triplicity: Sun (day), Jupiter (night), Saturn (partner). "
            "Body: head, face, brain. Hot & dry. Masucline, diurnal. Abu Ma'shar describes Aries as choleric, "
            "impetuous, and courageous — the Ram charges forward, initiating the astrological year at the "
            "Vernal Equinox. Colours: red, white.",
        ),
        (
            "♉ Taurus — Al-Thawr (The Bull)",
            "Fixed Earth. Ruler: Venus. Exaltation: Moon. Triplicity: Venus (day), Moon (night), Mars (partner). "
            "Body: neck, throat, vocal cords. Cold & dry. Feminine, nocturnal. Al-Biruni notes Taurus as "
            "stable, patient, and sensual — the Bull is fixed in purpose, slow to anger, and deeply connected "
            "to the material world. Colours: pale green, lemon.",
        ),
        (
            "♊ Gemini — Al-Jawza' (The Twins)",
            "Mutable Air. Ruler: Mercury. Exaltation: —. Triplicity: Saturn (day), Mercury (night), Jupiter (partner). "
            "Body: shoulders, arms, hands, lungs. Hot & moist. Masculine, diurnal. Abu Ma'shar calls Gemini "
            "the sign of duality — eloquent, inquisitive, and mercurial in temperament. Connected to writing, "
            "commerce, and all forms of exchange. Colours: mixed, saffron.",
        ),
        (
            "♋ Cancer — Al-Sartan (The Crab)",
            "Cardinal Water. Ruler: Moon. Exaltation: Jupiter (according to Valens) / Venus (according to "
            "Egyptian tradition). Triplicity: Venus (day), Mars (night), Moon (partner). "
            "Body: chest, breasts, stomach. Cold & moist. Feminine, nocturnal. Al-Biruni describes Cancer "
            "as receptive, nurturing, and protective — the Crab withdraws and holds close. The Moon's own "
            "sign, deeply connected to memory, ancestry, and the tides of emotion. Colours: green, russet.",
        ),
        (
            "♌ Leo — Al-Asad (The Lion)",
            "Fixed Fire. Ruler: Sun. Exaltation: —. Triplicity: Sun (day), Jupiter (night), Saturn (partner). "
            "Body: heart, spine, upper back. Hot & dry. Masculine, diurnal. Abu Ma'shar calls Leo the sign "
            "of kingship — magnanimous, proud, and creative. The Sun's throne, conferring dignity, leadership, "
            "and a generous spirit. Lovers of spectacle and the stage of life. Colours: gold, purple.",
        ),
        (
            "♍ Virgo — Al-Sunbulah (The Ear of Grain)",
            "Mutable Earth. Ruler: Mercury. Exaltation: Mercury (according to some). Triplicity: Venus (day), "
            "Moon (night), Mars (partner). Body: abdomen, intestines, digestive system. Cold & dry. Feminine "
            "nocturnal. Al-Biruni says Virgo is analytical, meticulous, and service-oriented — the harvest "
            "maiden who sorts wheat from chaff. Connected to health, craft, and detailed work. Colours: dark "
            "blue, speckled.",
        ),
        (
            "♎ Libra — Al-Mizan (The Scales)",
            "Cardinal Air. Ruler: Venus. Exaltation: Saturn. Triplicity: Saturn (day), Mercury (night), "
            "Jupiter (partner). Body: kidneys, lower back, skin. Hot & moist. Masculine, diurnal. Abu Ma'shar "
            "describes Libra as just, refined, and harmonious — the Scales weigh all things in balance. The "
            "Autumnal Equinox falls here, marking the descent into the darker half of the year. Colours: "
            "sky blue, green.",
        ),
        (
            "♏ Scorpio — Al-Aqrab (The Scorpion)",
            "Fixed Water. Ruler: Mars (traditional), Pluto (modern). Exaltation: —. Triplicity: Venus (day), "
            "Mars (night), Moon (partner). Body: reproductive organs, bladder, genitals. Cold & moist. "
            "Feminine, nocturnal. Al-Biruni describes Scorpio as intense, secretive, and transformative — "
            "the Scorpion's sting is both defensive and catalytic. The sign of deep mysteries, occult power, "
            "and regeneration. Colours: deep red, black.",
        ),
        (
            "♐ Sagittarius — Al-Qaws (The Bow)",
            "Mutable Fire. Ruler: Jupiter. Exaltation: —. Triplicity: Sun (day), Jupiter (night), Saturn (partner). "
            "Body: thighs, hips, liver. Hot & dry. Masculine, diurnal. Abu Ma'shar calls Sagittarius the "
            "seeker — philosophical, adventurous, and aspiring toward higher truth. The Archer aims beyond "
            "the horizon, patron of travellers, scholars, and visionaries. Colours: yellow, light green.",
        ),
        (
            "♑ Capricorn — Al-Jady (The Goat)",
            "Cardinal Earth. Ruler: Saturn. Exaltation: Mars. Triplicity: Venus (day), Moon (night), Mars (partner). "
            "Body: knees, bones, skin. Cold & dry. Feminine, nocturnal. Al-Biruni notes Capricorn as "
            "ambitious, disciplined, and enduring — the Sea-Goat climbs the mountain with patient resolve. "
            "Saturn's domicile, conferring authority, structure, and the wisdom earned through time. "
            "Colours: black, dark brown.",
        ),
        (
            "♒ Aquarius — Al-Dalw (The Water-Bearer)",
            "Fixed Air. Ruler: Saturn (traditional), Uranus (modern). Exaltation: —. Triplicity: Saturn (day), "
            "Mercury (night), Jupiter (partner). Body: calves, ankles, circulatory system. Hot & moist. "
            "Masculine, diurnal. Abu Ma'shar calls Aquarius the humanitarian — innovative, detached, and "
            "visionary. The Water-Bearer pours forth knowledge for the collective, bound to friendship, "
            "community, and sudden insight. Colours: sky blue, electric blue.",
        ),
        (
            "♓ Pisces — Al-Hut (The Fishes)",
            "Mutable Water. Ruler: Jupiter (traditional), Neptune (modern). Exaltation: Venus. Triplicity: "
            "Venus (day), Mars (night), Moon (partner). Body: feet, lymphatic system. Cold & moist. Feminine, "
            "nocturnal. Al-Biruni describes Pisces as dreamy, compassionate, and boundaryless — two fishes "
            "swimming in opposite directions, yet bound together. The sign of mysticism, imagination, and "
            "dissolution of the ego. Colours: sea green, lavender.",
        ),
    ],

    "Planets": [
        (
            "The Seven Traditional Planets — Al-Kawakib al-Sayyarah",
            (
                "Traditional astrology recognises seven visible planets (including the Sun and Moon as "
                "luminaries). Each planet has a distinct nature, combining the Aristotelian qualities "
                "(hot/cold, wet/dry) and is classified as benefic (beneficial), malefic (harmful), or "
                "neutral. Abu Ma'shar al-Balkhi in his Kitab al-Madkhal al-Kabir (Great Introduction) "
                "devoted extensive chapters to the planets' natures in each sign, their triplicities, "
                "and their effects on worldly affairs.\n\n"
                "Al-Biruni's Elements of the Art of Astrology provides a clear system: planets are "
                "judged by their essential dignity, house placement, aspects, and motion. The benefics "
                "are Jupiter and Venus; the malefics are Saturn and Mars; Mercury partakes of whichever "
                "planet it is configurated with. The luminaries — Sun and Moon — are the primary "
                "indicators of the soul and the body respectively."
            ),
        ),
        (
            "☉ Sun — Al-Shams",
            "Hot & dry. Masculine, diurnal. Ruler of Leo. Exalted in Aries. Joy in the 9th House. "
            "Represents: essence, vitality, the father, authority, kingship, the heart, consciousness. "
            "Abu Ma'shar: 'The Sun is the king of the heavens, giving life and light to all things.' "
            "Colour: gold, yellow. Metal: gold. Day: Sunday. Speed: ~1°/day.",
        ),
        (
            "☽ Moon — Al-Qamar",
            "Cold & moist. Feminine, nocturnal. Ruler of Cancer. Exalted in Taurus. Joy in the 3rd House. "
            "Represents: the body, emotions, the mother, memory, the public, change, tides. "
            "Al-Biruni: 'The Moon is the swiftest of the planets, receiving the light of the Sun and "
            "distributing it downward into the sublunar world.' Speed: ~13°/day (fastest).",
        ),
        (
            "☿ Mercury — Utarid",
            "Cold & dry (morning), hot & moist (evening). Neutral, convertible. Ruler of Gemini & Virgo. "
            "Exalted in Virgo (some say Aquarius). Joy in the 1st House. Represents: mind, speech, "
            "commerce, writing, travel, wit, thievery. Abu Ma'shar: 'Mercury is the scribe of the "
            "heavens, adapting to whomever he accompanies.' Speed: up to ~2°/day.",
        ),
        (
            "♀ Venus — Al-Zuharah",
            "Cold & moist (evening), hot & moist (morning). Feminine, nocturnal. Lesser Benefic. "
            "Ruler of Taurus & Libra. Exalted in Pisces. Joy in the 5th House. Represents: love, "
            "beauty, pleasure, art, luxury, friendship, attraction. Al-Biruni: 'Venus signifies "
            "marriage, adornment, pleasant things, and the attainment of desires.' Speed: ~1.2°/day.",
        ),
        (
            "♂ Mars — Al-Mirrikh",
            "Hot & dry. Masculine, diurnal. Lesser Malefic. Ruler of Aries (and Scorpio in traditional). "
            "Exalted in Capricorn. Joy in the 6th House. Represents: energy, war, conflict, courage, "
            "passion, surgery, iron, fire. Abu Ma'shar: 'Mars is the bringer of strife, the severer, "
            "the commander of armies.' Speed: ~0.5°/day.",
        ),
        (
            "♃ Jupiter — Al-Mushtari",
            "Hot & moist. Masculine, diurnal. Greater Benefic. Ruler of Sagittarius & Pisces (traditional). "
            "Exalted in Cancer. Joy in the 11th House. Represents: fortune, expansion, wisdom, "
            "generosity, law, religion, prosperity. Al-Biruni: 'Jupiter signifies justice, faith, "
            "knowledge, begetting of children, and increase of goods.' Speed: ~0.08°/day.",
        ),
        (
            "♄ Saturn — Zuhal",
            "Cold & dry. Masculine, diurnal. Greater Malefic. Ruler of Capricorn & Aquarius (traditional). "
            "Exalted in Libra. Joy in the 12th House. Represents: limitation, time, discipline, "
            "structure, ancestry, melancholy, old age, solitude. Abu Ma'shar: 'Saturn is the lord of "
            "the hidden, the tester of the soul through delay and hardship.' Speed: ~0.03°/day.",
        ),
    ],

    "Houses": [
        (
            "The Twelve Houses — Al-Buyut",
            (
                "The houses (buyut, 'dwelling places') divide the ecliptic into twelve sections of "
                "experience, each governing a specific domain of life. In Hellenistic and Medieval "
                "Islamic astrology, houses are classified as angular (1st, 4th, 7th, 10th — strongest), "
                "succedent (2nd, 5th, 8th, 11th — moderate), and cadent (3rd, 6th, 9th, 12th — weakest). "
                "\n\n"
                "Al-Biruni's Elements gives clear delineations for each house. Abu Ma'shar further "
                "elaborated on the 'joys' of the planets — specific houses where each planet rejoices "
                "and operates with particular strength. The Whole Sign house system was standard "
                "in Hellenistic times; later Medieval Islamic astrologers like Al-Biruni described "
                "both Whole Sign and quadrant (Alcabitius/Porphyry) systems."
            ),
        ),
        (
            "1st House — The Ascendant (Al-Tali')",
            "Angular. Natural sign: Aries. Joy of Mercury. Represents: the self, the body, "
            "temperament, physical appearance, the start of life. The rising sign sets the entire "
            "tone of the chart. In Hellenistic astrology, the Ascendant lord is the principal "
            "indicator of the native's character and vitality.",
        ),
        (
            "2nd House — Property (Al-Mal)",
            "Succedent. Natural sign: Taurus. Represents: wealth, movable possessions, income, "
            "resources, self-worth. Al-Biruni: 'The Second House indicates livelihood, substance, "
            "and that which a man acquires by his own effort.'",
        ),
        (
            "3rd House — Brethren (Al-Ikhwah)",
            "Cadent. Natural sign: Gemini. Joy of the Moon. Represents: siblings, short journeys, "
            "communication, neighbours, letters, news. The Moon's joy here connects daily "
            "intercourse with the rhythms of change.",
        ),
        (
            "4th House — Parents (Al-Aba')",
            "Angular. Natural sign: Cancer. Represents: the father (Hellenistic) or the mother "
            "(modern), ancestry, homeland, the home, real estate, the end of life. The 'Imum "
            "Coeli' (midnight point) marks the deepest foundation of the chart.",
        ),
        (
            "5th House — Children (Al-Walad)",
            "Succedent. Natural sign: Leo. Joy of Venus. Represents: children, pleasure, "
            "creativity, romance, speculation, entertainment. Venus rejoices here in the realm "
            "of pleasure and artistic expression.",
        ),
        (
            "6th House — Servants (Al-Khadam)",
            "Cadent. Natural sign: Virgo. Joy of Mars. Represents: servants, employees, health, "
            "illness, small animals, labour. Mars' joy here channels his aggression into work "
            "and service — but also brings the potential for sickness.",
        ),
        (
            "7th House — Marriage (Al-Zawaj)",
            "Angular. Natural sign: Libra. Represents: marriage, partnerships, open enemies, "
            "contracts, the other. The Descendant (setting point) defines one-to-one relationships "
            "and the nature of those we attract.",
        ),
        (
            "8th House — Death (Al-Mawt)",
            "Succedent. Natural sign: Scorpio. Represents: death, inheritance, transformation, "
            "other people's money, sex, the occult. Al-Biruni: 'The Eighth House indicates the "
            "duration of life, the nature of death, and the goods of the dead.'",
        ),
        (
            "9th House — Travel & Faith (Al-Safar)",
            "Cadent. Natural sign: Sagittarius. Joy of the Sun. Represents: long journeys, "
            "religion, philosophy, higher education, dreams, prophecy, the divine. The Sun's joy "
            "here connects to the search for higher truth. Abu Ma'shar: 'The Ninth House pertains "
            "to the knowledge of religion, wisdom, and divination.'",
        ),
        (
            "10th House — Honour (Al-Sharaf)",
            "Angular. Natural sign: Capricorn. Represents: career, honour, reputation, authority, "
            "the mother (Hellenistic), public standing, achievements. The Midheaven (MC) is the "
            "most elevated point, showing one's peak expression in the world.",
        ),
        (
            "11th House — Friends (Al-Sadaqah)",
            "Succedent. Natural sign: Aquarius. Joy of Jupiter. Represents: friends, hopes, "
            "wishes, allies, social networks, patronage. Jupiter's joy here signifies the "
            "beneficence of good associations and the fulfilment of aspirations.",
        ),
        (
            "12th House — Enmity (Al-Ida')",
            "Cadent. Natural sign: Pisces. Joy of Saturn. Represents: hidden enemies, "
            "imprisonment, seclusion, self-undoing, institutions, karma, the collective "
            "unconscious. Saturn's joy here tests through solitude, restriction, and shadow work.",
        ),
    ],

    "Aspects": [
        (
            "The Ptolemaic Aspects — Al-Nazarat",
            (
                "Aspects (nazarat, 'viewings') are angular relationships between planets that "
                "determine how their energies interact. Claudius Ptolemy in the Tetrabiblos codified "
                "the five major aspects based on the harmonic divisions of the 360° circle. "
                "Al-Biruni and Abu Ma'shar followed this system, emphasising that aspects are "
                "most powerful when formed by sign (sign-based) rather than by degree alone.\n\n"
                "In Traditional astrology, only the five Ptolemaic aspects are used (the modern "
                "minor aspects — semi-sextile, quincunx, etc. — are not part of the traditional "
                "toolkit). The applying/separating distinction is crucial: applying aspects (where "
                "the faster planet approaches perfect aspect) are unfulfilled and active; separating "
                "aspects (past perfect) show completed matters."
            ),
        ),
        (
            "☌ Conjunction — 0° (Al-Ijtima')",
            "The strongest aspect. Two planets at the same degree blend their natures entirely. "
            "If one is benefic and one malefic, they 'mix' according to the nature of the stronger. "
            "The closer the orb (max 8° for luminaries, 5-6° for planets), the more powerful. "
            "Conjunctions with the Sun (combustion) severely weaken a planet — it is said to be "
            "'under the beams' (within 15°) and diminished in power.",
        ),
        (
            "✶ Sextile — 60° (Al-Tasdis)",
            "Harmonious aspect. Signs of the same triplicity (e.g. Fire to Air, Earth to Water). "
            "Indicates opportunity, cooperation, and flow — but requires conscious activation as "
            "it is a 'soft' aspect. Al-Biruni: 'The sextile indicates love and friendship, but "
            "weaker than the trine.' Accepted orb: up to 5-6°.",
        ),
        (
            "□ Square — 90° (Al-Tarbi')",
            "Hard aspect. Signs of the same quadruplicity (modality) but differing triplicity. "
            "Indicates tension, conflict, and challenge — the friction that drives growth. "
            "Abu Ma'shar: 'The square brings enmity, separation, and difficulty, yet it is the "
            "aspect of action and accomplishment through struggle.' Accepted orb: up to 6-7°.",
        ),
        (
            "△ Trine — 120° (Al-Tathlith)",
            "Most harmonious aspect. Signs of the same triplicity (element). Indicates natural "
            "talent, ease, and effortless flow. Often called the 'free lunch' aspect — too many "
            "trines can indicate lack of drive. Al-Biruni: 'The trine is the aspect of perfect "
            "concord, love, and agreement.' Accepted orb: up to 7-8°.",
        ),
        (
            "☍ Opposition — 180° (Al-Muqabilah)",
            "Hardest aspect. Signs of the same quality (mutable/fixed/cardinal) but opposite "
            "elements. Indicates polarisation, projection, and the need for integration. The "
            "two planets are at maximum separation, forcing awareness of the 'other.' "
            "Accept orb: up to 7-8°. An opposition involving the Sun-Moon axis is the Full Moon, "
            "a time of heightened tension and illumination.",
        ),
        (
            "Applying vs. Separating — Al-Iqbal wa al-Idbar",
            "A planet is 'applying' to aspect when it is moving toward perfecting the aspect "
            "with a slower planet. It is 'separating' when it has already perfected and moves away. "
            "Applying aspects are considered more powerful — they represent potential that is yet "
            "to manifest. Separating aspects are spent, their effects already woven into the past. "
            "In horary and electional astrology, applying aspects between significators indicate "
            "the matter will come to pass.",
        ),
    ],

    "Planetary Dignities": [
        (
            "Essential Dignity & Debility — Al-Sharaf wa al-Hubut",
            (
                "Essential dignity measures a planet's inherent strength based on its zodiacal "
                "position. In Hellenistic and Medieval Islamic astrology, dignity is the single "
                "most important factor in judging a planet's capacity to act effectively. "
                "There are five essential dignities (domicile, exaltation, triplicity, term, face) "
                "and two debilities (detriment, fall). Al-Biruni provides a complete table of "
                "dignities in his Elements, and Abu Ma'shar's Great Introduction devotes extensive "
                "chapters to planetary strength by dignity.\n\n"
                "The traditional system of point-scoring (sometimes known as 'Al-Biruni's allotments') "
                "assigns: Domicile 5, Exaltation 4, Triplicity 3, Term 2, Face 1. A planet with "
                "more dignities than debilities is 'supported'; one with more debilities is 'weakened.'"
            ),
        ),
        (
            "♔ Domicile — Al-Watan (Home)",
            "A planet rules the sign. The strongest dignity. The planet is 'at home' — fully "
            "expressive and unconstrained. Example: Mars in Aries or Scorpio, Venus in Taurus "
            "or Libra. Value: +5. The opposite sign is the planet's Detriment (al-ghurbah, "
            "'exile'), where the planet is uncomfortable and weak.",
        ),
        (
            "♕ Exaltation — Al-Sharaf (Elevation)",
            "A planet is 'exalted' in a specific sign where it acts with special honour and "
            "power — like a visiting dignitary. Example: Sun in Aries (exaltation), Moon in "
            "Taurus. Value: +4. The opposing point (7 signs later) is the Fall (al-hubut, "
            "'descent'), where the planet is debilitated.",
        ),
        (
            "♰ Triplicity — Al-Muthallathah",
            "Planets ruling an element triplicity diurnally and nocturnally. In Medieval "
            "practice, each triplicity has three rulers: one for day charts, one for night "
            "charts, and a 'participating' ruler. Value: +3. Abu Ma'shar gives the triplicity "
            "rulers in his Great Introduction, and they differ slightly from Ptolemy's.",
        ),
        (
            "♨ Term — Al-Hadd (Bound)",
            "Each sign is divided into 5 unequal 'terms' or bounds (hudud, 'boundaries'), "
            "each ruled by a different planet. This system dates back to the Egyptian "
            "astrologers. The Chaldean (Babylonian) terms and Egyptian terms differ slightly; "
            "Ptolemy and Al-Biruni preferred the Egyptian terms. Value: +2 per term.",
        ),
        (
            "☷ Face — Al-Wajh (Countenance)",
            "Each sign is divided into 3 equal decans (10° each), each ruled by a planet. "
            "This is the weakest dignity. The decan rulers follow the Chaldean order through "
            "the signs. Value: +1. In Abu Ma'shar's system, the decans have specific talismanic "
            "and imaginal qualities.",
        ),
        (
            "Accidental Dignity — Al-Sharaf al-Aradi",
            "Strength gained from circumstance rather than essence. A planet may be essentially "
            "weak but accidentally strong (or vice versa). Accidental dignities include:\n"
            "  • Angular placement (1st, 10th, 7th, 4th houses) — strongest\n"
            "  • Direct motion (vs. retrograde)\n"
            "  • Fast motion (above average daily speed)\n"
            "  • Being in a house of its joy\n"
            "  • Being oriental/occidental (rising before/setting after the Sun)\n"
            "  • Not combust (within 8°30' of the Sun)\n"
            "  • Not in the Via Combusta (15° Libra — 15° Scorpio)\n"
            "  • Cazimi (within 17' of the Sun) — extreme strength",
        ),
        (
            "Essential Debilities",
            "• Detriment (al-ghurbah): the sign opposite a planet's domicile. The planet is "
            "in 'exile', working against its own nature. Value: -5.\n"
            "• Fall (al-hubut): the sign opposite a planet's exaltation. The planet is "
            "'descended', humiliated and weak. Value: -4.\n"
            "• Peregrine (al-munqati'): a planet with no essential dignity — not domicile, "
            "exaltation, triplicity, term, or face. It wanders without support, vulnerable "
            "to malefics. Abu Ma'shar: 'A peregrine planet is like a stranger in a foreign "
            "land with no allies.'",
        ),
    ],

    "Chart Interpretation": [
        (
            "The Four Pillars of Hellenistic Interpretation",
            (
                "Traditional chart reading rests on four pillars: the Planet, its Sign placement, "
                "its House placement, and its Aspects. This fourfold method was formalised in "
                "the Hellenistic period (c. 1st c. BCE — 6th c. CE) by authors such as Dorotheus "
                "of Sidon, Vettius Valens, and Claudius Ptolemy, and carried forward by Medieval "
                "Islamic astrologers including Abu Ma'shar and Al-Biruni.\n\n"
                "Al-Biruni's method: First consider the planet's essential dignity in the sign. "
                "Then its house placement and angularity. Then the aspects it receives — especially "
                "from the benefics and malefics. Finally, synthesise: what does this planet 'mean' "
                "in this chart, and how strongly can it deliver?"
            ),
        ),
        (
            "Step 1: The Ascendant and the Lord of the Chart",
            "The Ascendant (rising sign) sets the stage. Its planetary ruler is the Oikodespotes "
            "(Hellenistic) or the 'lord of the geniture' — the single most important planet in "
            "the chart. Abu Ma'shar advises: 'First examine the rising sign and its lord, then "
            "the Sun's position for the soul, then the Moon for the body, then the Lot of Fortune "
            "for worldly success.'",
        ),
        (
            "Step 2: The Sun and Moon — The Lights",
            "The Sun represents the soul (al-nafs al-natiqah, 'rational soul'), the conscious "
            "self, and the father. Its sign, house, and aspects reveal the native's essential "
            "nature and life path. The Moon represents the body, the emotions, the mother, and "
            "the native's instinctual responses. The configuration between Sun and Moon — the "
            "Phase of the Moon at birth — is a critical indicator of the soul's intention in "
            "this incarnation.",
        ),
        (
            "Step 3: The Five Planets and Their Configurations",
            "After the luminaries, examine Mercury (mind, communication), Venus (love, values), "
            "Mars (drive, action), Jupiter (fortune, expansion), and Saturn (limitation, "
            "structure). Note which are in their own dignities vs. debilities. Observe the "
            "aspects between them. A planet receiving a trine or sextile from Jupiter is "
            "strengthened; one receiving a square or opposition from Saturn is tested.",
        ),
        (
            "Step 4: The Houses and Their Lords",
            "Each house governs a domain of life. The condition of that house's ruling planet "
            "(its sign, house, and aspects) tells the story of that domain. For example, the "
            "ruler of the 7th House indicates the nature of marriage; the ruler of the 2nd "
            "House reveals the source and stability of income. Vettius Valens emphasised that "
            "the 'testimony' of multiple planets converging on a single house or topic is the "
            "most reliable indicator.",
        ),
        (
            "Step 5: The Lots (Al-Siham)",
            "The Lots (or Parts) are calculated points derived from the positions of two planets "
            "and the Ascendant. The most important is the Lot of Fortune (al-sahm al-ikbal), "
            "calculated as Ascendant + Moon - Sun (day), or Ascendant + Sun - Moon (night). "
            "The Lot of Spirit (al-sahm al-ghayb) — Ascendant + Sun - Moon (day), or Ascendant "
            "+ Moon - Sun (night) — indicates the native's deeper purpose and spiritual path. "
            "Abu Ma'shar gives extensive treatment of the lots in his Great Introduction.",
        ),
    ],

    "Transits": [
        (
            "Transits in Traditional Perspective — Al-Sayr",
            (
                "In Traditional astrology, transits (sayr, 'motion') are interpreted differently "
                "than in modern psychological astrology. The emphasis is on planetary natures and "
                "timing rather than 'growth' or 'evolution.' A transit of Saturn is not an "
                "'opportunity for growth' — it is a period of restriction and testing whose "
                "outcome depends on the condition of the transited planet in the natal chart.\n\n"
                "Al-Biruni distinguished between major (al-sayr al-kabir) and minor (al-sayr "
                "al-saghir) transits. Abu Ma'shar's Book of Thousands set out the theory of "
                "planetary periods (firdaria) which remain in use today for timing events."
            ),
        ),
        (
            "The Outer Planets & The Lights",
            "Saturn transits: Lasting ~2.5 years per sign. Return at age 29-30 (coming of age), "
            "second return at ~58-60 (wisdom and harvest). Saturn transits to the angles or "
            "luminaries are the most significant timing markers in Traditional astrology.\n\n"
            "Jupiter transits: ~1 year per sign. Jupiter's return at age 12 — expansion and "
            "opportunity. A generally beneficial transit, but can over-expand if Jupiter is "
            "poorly placed in the natal chart.\n\n"
            "Mars transits: ~2 months per sign. Quick and sharp. Triggers events and conflict. "
            "Mars retrograde may frustrate and delay.\n\n"
            "Sun transits: ~1 month per sign. Annual Solar Return marks the birthday year's "
            "theme.\n\n"
            "Moon transits: ~2.5 days per sign. The fastest trigger — emotional weather.",
        ),
        (
            "Transiting Aspects — Al-Sayr bi al-Nazar",
            "In Medieval Islamic practice, a transit is not simply a planet moving over a natal "
            "point — it is the activation of a running (or directional) time lord system. The "
            "most common methods:\n\n"
            "1. Firdaria (Abu Ma'shar's period system): Each period of life is ruled by a "
            "planet in a fixed sequence. Transits during that planet's period are amplified.\n\n"
            "2. Solar Returns (al-tahwil al-shamsi): The moment the Sun returns to its natal "
            "position. This chart is erected for the present location and interpreted as the "
            "annual theme.\n\n"
            "3. Lunar Returns: The monthly Moon return is used for finer timing, especially "
            "in electional work.",
        ),
        (
            "Practical Transit Reading",
            "1. Note the condition of the transiting planet itself (dignity, speed, aspect).\n"
            "2. Note the condition of the natal planet being activated (its essential and "
            "accidental dignity).\n"
            "3. A benefic transiting a well-placed natal planet is excellent.\n"
            "4. A malefic transiting a debilitated natal planet is challenging.\n"
            "5. A malefic transiting a well-dignified natal planet may bring difficulty but "
            "the native can handle it.\n"
            "6. A benefic transiting a debilitated natal planet may soften the difficulty but "
            "not remove it entirely.\n"
            "7. Watch transits to the Ascendant, MC, and their rulers — these are the most "
            "personal and powerful.",
        ),
    ],

    "Electional Astrology": [
        (
            "Foundations of Electional Astrology — Al-Ikhtiyarat",
            (
                "Electional astrology (ikhtiyarat, 'choices') is the art of selecting the most "
                "favourable moment to begin an undertaking. It was highly developed in the "
                "Medieval Islamic tradition, particularly in the Ghayat al-Hakim (Picatrix), "
                "the works of Abu Ma'shar, and later in Ahmad al-Buni's Shams al-Ma'arif. "
                "Al-Biruni devoted substantial sections of his Elements to elections.\n\n"
                "The core principle: align the celestial quality with the nature of the act. "
                "A wedding requires a Venus-Moon election; a coronation requires a Sun-Jupiter "
                "election; a battle requires a Mars election."
            ),
        ),
        (
            "General Rules for Elections",
            "1. Choose the appropriate planet's day and hour (e.g. Venus on Friday, hour of Venus).\n"
            "2. The Moon is the single most important factor: place it well. It should be:\n"
            "   • Waxing (increasing in light, from New to Full)\n"
            "   • Above the horizon (visible)\n"
            "   • In a sign compatible with the matter\n"
            "   • Free from malefic aspect (especially within 3°)\n"
            "3. Avoid the Moon in Via Combusta (15° Libra — 15° Scorpio).\n"
            "4. Place the Ascendant in a sign appropriate to the matter.\n"
            "5. Put the ruler of the matter in good essential and accidental dignity.\n"
            "6. The lord of the hour should agree with the nature of the election.",
        ),
        (
            "Planetary Elections by Nature",
            "☉ Sun: Coronations, promotions, appointments, creative work, seeking favour from "
            "authorities. Day: Sunday. Ascendant: Leo.\n\n"
            "☽ Moon: Beginnings, travel, agriculture, medicine, domestic matters, planting, "
            "day-to-day ventures. Day: Monday. Ascendant: Cancer.\n\n"
            "☿ Mercury: Writing, contracts, study, teaching, commerce, travel, negotiation. "
            "Day: Wednesday. Ascendant: Gemini/Virgo.\n\n"
            "♀ Venus: Marriage, love, art, music, friendship, adornment, feasts. Day: Friday. "
            "Ascendant: Taurus/Libra.\n\n"
            "♂ Mars: War, litigation, competition, surgery, physical exercise, sexual initiation. "
            "Day: Tuesday. Ascendant: Aries/Scorpio.\n\n"
            "♃ Jupiter: Religious ceremonies, legal matters, charity, coronations, expansion, "
            "wealth, education. Day: Thursday. Ascendant: Sagittarius/Pisces.\n\n"
            "♄ Saturn: Building, agriculture, real estate, contracts of long duration, binding "
            "obligations, retreat, magical binding. Day: Saturday. Ascendant: Capricorn/Aquarius.",
        ),
        (
            "The 28 Lunar Mansions (Manazil al-Qamar)",
            "In the Islamic electional tradition, the 28 Lunar Mansions (manazil al-qamar) are "
            "paramount. The Moon passes through one station per day (~13°20' each). Each mansion "
            "has a particular nature — favourable, neutral, or unfavourable — for specific "
            "activities. The Picatrix (Ghayat al-Hakim) devotes extensive chapters to the "
            "talismanic operations associated with each mansion.\n\n"
            "Examples:\n"
            "• Mansion 1 (Al-Sharatayn): Beginning journeys, planting, construction\n"
            "• Mansion 4 (Al-Dabaran): High honour, marriage, commerce\n"
            "• Mansion 8 (Al-Nathrah): Travel by land, marriage\n"
            "• Mansion 16 (Al-Zubanah): Avoid for love or travel; suitable for destruction\n"
            "• Mansion 24 (Al-Sadu Bala'): Destroying enemy schemes, separation\n"
            "• Mansion 28 (Al-Batn al-Hut): Fulfilling intentions, protection",
        ),
        (
            "Planetary Hours in Elections",
            "The planetary hours system divides day and night into 12 unequal hours each, "
            "ruled by the planets in Chaldean order (Saturn → Jupiter → Mars → Sun → Venus → "
            "Mercury → Moon). The first hour of sunrise is always ruled by the planet of the "
            "day. These hours are critical in electional work — an otherwise well-drafted "
            "election fails if the hour opposes the matter.\n\n"
            "Abu Ma'shar emphasised that the planetary hour should agree with both the "
            "Ascendant ruler and the Moon's position. When all three are in harmony, the "
            "election is considered 'radical' and certain to succeed.",
        ),
    ],

    "Traditional / Hellenistic Astrology": [
        (
            "Origins & History",
            (
                "Hellenistic astrology emerged in the Mediterranean basin around the 2nd century "
                "BCE, fusing Babylonian celestial omens with Egyptian decanic traditions and "
                "Greek philosophical concepts (especially Stoic sympathy and Aristotelian physics). "
                "It is the direct ancestor of Medieval Islamic, Renaissance, and modern Western "
                "astrology.\n\n"
                "The key innovation of Hellenistic astrology was the development of the birth "
                "chart (genethlialogy) as a systematic tool. Earlier traditions focused on "
                "omens and horary; the Greeks created a complete interpretive framework using "
                "planets, signs, houses, and aspects in a unified geometrical model."
            ),
        ),
        (
            "Major Hellenistic Authors",
            "• Claudius Ptolemy (c. 150 CE): Tetrabiblos. The single most influential astrological "
            "text in Western history. Established the framework for planetary dignities, aspects, "
            "and house meanings.\n\n"
            "• Vettius Valens (c. 150-175 CE): Anthologies. Nine books of practical charts and "
            "techniques. More detailed and less theoretical than Ptolemy — essential for "
            "understanding how Hellenistic astrology was actually practised.\n\n"
            "• Dorotheus of Sidon (c. 75 CE): Carmen Astrologicum. A didactic poem that deeply "
            "influenced Medieval Islamic astrology through its Arabic translation.\n\n"
            "• Firmicus Maternus (c. 335 CE): Mathesis. The last great Latin astrological "
            "compendium, preserving many earlier Greek techniques.\n\n"
            "• Paulus Alexandrinus (c. 378 CE): Introductory Matters. A concise handbook of "
            "Hellenistic technique, especially on the Lots and planetary condition.",
        ),
        (
            "Key Hellenistic Techniques",
            "• Whole Sign Houses: Each sign is one entire house. The Ascendant is the rising "
            "sign, and the houses follow sign by sign. The most ancient system.\n\n"
            "• Planetary Joys: Each of the seven planets has a house where it 'rejoices' and "
            "operates with special ease.\n\n"
            "• Sect (al-qismah): Day charts (Sun above horizon) vs. night charts (Sun below). "
            "The diurnal planets (Saturn, Jupiter, Sun) function better in day charts; "
            "nocturnal planets (Mars, Venus, Moon) in night charts. Mercury is convertible.\n\n"
            "• The Lots (Siham): Mathematical points derived from three positions, most "
            "importantly the Lot of Fortune and Lot of Spirit.\n\n"
            "• Firdaria (Abu Ma'shar's Periods): Time-lord system dividing life into planetary "
            "periods, each ruled by a planet for a specific number of years.\n\n"
            "• Annual Profections: The Ascendant advances one sign per year of life. Each year, "
            "the house whose sign the profected Ascendant falls into is 'activated' for that year.",
        ),
        (
            "Ptolemaic vs. Valens Approaches",
            "Ptolemy's astrology is philosophical and causal — planets act through their qualities "
            "(hot/cold/wet/dry) in a quasi-Aristotelian system. Valens is more empirical and "
            "divinatory — he records hundreds of nativities and judges each by its lot, the ruler "
            "of the terms, and planetary periods. Medieval Islamic astrologers like Abu Ma'shar "
            "synthesised both streams: the causal framework of Ptolemy and the practical techniques "
            "of Valens and Dorotheus.",
        ),
    ],

    "Medieval Islamic Astrology": [
        (
            "The Golden Age of Islamic Astrology (8th-13th c.)",
            (
                "The translation movement of the 8th-9th centuries (Bayt al-Hikmah, the House "
                "of Wisdom in Baghdad) brought Hellenistic texts into Arabic. Persian, Indian "
                "(Sindhind), and Hermetic traditions were also absorbed, creating a rich "
                "synthesis that later passed to Europe via Al-Andalus (Islamic Spain).\n\n"
                "Islamic astrologers did not merely translate — they innovated. They developed "
                "new techniques in conjunction theory, mundane astrology (al-ahkam 'ala al-sinin), "
                "and electional/talismanic astrology. The 'Great Introduction to Astrology' of "
                "Abu Ma'shar became the single most influential astrological work in the Latin "
                "Middle Ages."
            ),
        ),
        (
            "Abu Ma'shar al-Balkhi (Albumasar, 787-886 CE)",
            "Born in Balkh (modern Afghanistan), Abu Ma'shar was the most famous astrologer "
            "of the Abbasid court. His major works:\n\n"
            "• Kitab al-Madkhal al-Kabir (Great Introduction to Astrology): An eight-book "
            "masterwork covering the natures of planets, signs, houses, aspects, dignities, "
            "and world history. Latin translation made him 'Albumasar' — the authority cited "
            "by Albertus Magnus, Roger Bacon, and Dante.\n\n"
            "• Kitab al-Aluf (Book of Thousands): On planetary periods (firdaria) and the "
            "conjunctions of Saturn and Jupiter (the famous 'great conjunctions' theory of "
            "history).\n\n"
            "• De Magnis Coniunctionibus (On the Great Conjunctions): Abu Ma'shar's theory "
            "that the 20-year conjunctions of Saturn and Jupiter mark the rise and fall of "
            "dynasties, religions, and civilisations.\n\n"
            "• Kitab al-Mawalid (Book of Nativities): On birth charts.\n\n"
            "His method: synthesise Ptolemaic causality with Persian and Indian timing "
            "techniques. Every judgment rests on the condition of the planets by sign, house, "
            "aspect, and period.",
        ),
        (
            "Al-Biruni (973-1048 CE)",
            "Abu al-Rayhan Muhammad ibn Ahmad al-Biruni was a towering polymath — astronomer, "
            "mathematician, historian, and astrologer. Born in Khwarizm (modern Uzbekistan), "
            "he flourished in the court of Sultan Mahmud of Ghazni. His astrological magnum opus:\n\n"
            "• Kitab al-Tafhim li-Awa'il Sina'at al-Tanjim (The Book of Instruction in the "
            "Elements of the Art of Astrology, 1029 CE): A question-and-answer manual that "
            "covers geometry, astronomy, calendrics, planetary motion, aspects, dignities, "
            "houses, nativities, elections, and interrogations (horary). It is the most lucid "
            "and accessible Medieval Islamic astrological text.\n\n"
            "Al-Biruni's approach is systematic and skeptical — he distinguishes between "
            "mathematical astronomy (ilm al-hay'ah) and astrological judgment (ilm al-ahkam), "
            "and insists the astrologer first master astronomy before making any judgment. "
            "He provides clear tables of dignities, aspects, and house meanings that remain "
            "the standard reference for Traditional astrologers today.",
        ),
        (
            "Other Major Islamic Astrologers",
            "• Mash'allah ibn Athari (c. 740-815 CE): Jewish-Persian astrologer who advised "
            "the founding of Baghdad (762 CE). Works on elections, nativities, conjunctions.\n\n"
            "• Omar Tiberias (Umar al-Tabari, c. 800 CE): Author of Three Books on Nativities, "
            "widely influential in Latin translation.\n\n"
            "• Sahl ibn Bishr (Zael, c. 820 CE): On interrogations (horary), elections, and "
            "the interpretation of times.\n\n"
            "• Ahmad al-Buni (d. 1225 CE): Shams al-Ma'arif al-Kubra (The Great Sun of "
            "Knowledge). The most important Arabic grimoire, blending astrology with letter "
            "magic (ilm al-huruf), talismans, and Sufi mysticism.\n\n"
            "• Al-Qabisi (Alcabitius, c. 950 CE): His Introduction to Astrology was the "
            "standard university textbook on astrology in Medieval Europe.\n\n"
            "• The Ghayat al-Hakim (Picatrix, c. 11th c.): Anonymous Andalusian compilation "
            "of astrological magic, spirits, talismans, and planetary hours. Deeply influential "
            "on Renaissance occult philosophy.",
        ),
        (
            "Key Islamic Contributions to Astrological Technique",
            "1. The Great Conjunctions theory (Abu Ma'shar): Political and religious history "
            "is governed by the conjunctions of Saturn and Jupiter every 20 years.\n\n"
            "2. Firdaria (planetary periods): A time-lord system of Egyptian origin, elaborated "
            "by Abu Ma'shar, allocating each period of life to a planet.\n\n"
            "3. Lunar Mansions (Manazil al-Qamar): The 28 mansions for electional and talismanic "
            "work, culminating in the Picatrix tradition.\n\n"
            "4. Planetary Hours refinement: Islamic astrologers systematised the unequal "
            "planetary hours and their talismanic correspondences.\n\n"
            "5. Triplicity rulers: The system of triplicity rulers for day and night was "
            "standardised and transmitted to Europe.\n\n"
            "6. The combination of astrology with lettrism (ilm al-huruf): Al-Buni and others "
            "correlated planets with Arabic letters, divinatory squares (wafq), and divine names.",
        ),
    ],
}

# Flat list of section names for navigation
SECTION_NAMES = [
    "Zodiac Signs",
    "Planets",
    "Houses",
    "Aspects",
    "Planetary Dignities",
    "Chart Interpretation",
    "Transits",
    "Electional Astrology",
    "Traditional / Hellenistic Astrology",
    "Medieval Islamic Astrology",
]
