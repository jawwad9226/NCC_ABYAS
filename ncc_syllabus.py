"""
NCC Syllabus Configuration
Comprehensive syllabus data organized for quiz generation and content management
"""

from typing import Dict, List, Tuple
from enum import Enum

class DifficultyLevel(Enum):
    """Difficulty levels for NCC syllabus"""
    JD_JW = "JD/JW"  # Junior Division/Junior Wing
    SD_SW = "SD/SW"  # Senior Division/Senior Wing
    BOTH = "BOTH"    # Common to both levels

class Wing(Enum):
    """NCC Wings"""
    COMMON = "COMMON"
    ARMY = "ARMY"
    NAVY = "NAVY"
    AIR_FORCE = "AIR_FORCE"

# Complete NCC Syllabus Structure
NCC_SYLLABUS = {
    "CHAPTER-I": {
        "title": "NCC",
        "wing": Wing.COMMON,
        "sections": {
            "SECTION-1": {
                "title": "General",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "History and formation of NCC",
                    "Aims and objectives of NCC",
                    "NCC motto and pledge",
                    "Organization structure"
                ],
                "learning_objectives": [
                    "Understanding NCC's role in nation building",
                    "Knowledge of NCC history and evolution",
                    "Comprehension of NCC values and principles"
                ]
            },
            "SECTION-2": {
                "title": "Organisation",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "NCC organizational hierarchy",
                    "Command structure",
                    "Units and formations",
                    "Administrative setup"
                ],
                "learning_objectives": [
                    "Understanding organizational structure",
                    "Knowledge of command hierarchy",
                    "Awareness of administrative processes"
                ]
            },
            "SECTION-3": {
                "title": "Philosophy of Training",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Training methodology",
                    "Character development principles",
                    "Leadership development approach",
                    "Discipline and values"
                ],
                "learning_objectives": [
                    "Understanding training philosophy",
                    "Appreciation of character building",
                    "Knowledge of leadership principles"
                ]
            },
            "SECTION-4": {
                "title": "NCC Song",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "NCC song lyrics",
                    "Meaning and significance",
                    "Proper rendering",
                    "Occasions for singing"
                ],
                "learning_objectives": [
                    "Memorization of NCC song",
                    "Understanding its significance",
                    "Proper presentation skills"
                ]
            },
            "SECTION-5": {
                "title": "Incentives for NCC Cadets",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Academic benefits",
                    "Career advantages",
                    "Certificate benefits",
                    "Selection preferences"
                ],
                "learning_objectives": [
                    "Knowledge of available incentives",
                    "Understanding career benefits",
                    "Motivation for participation"
                ]
            }
        }
    },
    
    "CHAPTER-II": {
        "title": "NATIONAL INTEGRATION",
        "wing": Wing.COMMON,
        "sections": {
            "SECTION-1": {
                "title": "Indian History and Culture",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Ancient Indian civilization",
                    "Medieval period",
                    "Freedom struggle",
                    "Cultural heritage"
                ],
                "learning_objectives": [
                    "Understanding Indian heritage",
                    "Knowledge of historical events",
                    "Appreciation of cultural diversity"
                ]
            },
            "SECTION-2": {
                "title": "Religion and Customs of India",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Major religions in India",
                    "Religious festivals",
                    "Traditional customs",
                    "Cultural practices"
                ],
                "learning_objectives": [
                    "Understanding religious diversity",
                    "Respect for all religions",
                    "Knowledge of customs and traditions"
                ]
            },
            "SECTION-3": {
                "title": "Unity in Diversity",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Concept of unity in diversity",
                    "Regional variations",
                    "Language diversity",
                    "Cultural synthesis"
                ],
                "learning_objectives": [
                    "Understanding India's diversity",
                    "Appreciation of unity concept",
                    "Tolerance and acceptance"
                ]
            },
            "SECTION-4": {
                "title": "National Integration and its Importance",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Meaning of national integration",
                    "Importance for nation building",
                    "Challenges to integration",
                    "Role of youth"
                ],
                "learning_objectives": [
                    "Understanding national integration",
                    "Recognizing its importance",
                    "Commitment to national unity"
                ]
            },
            "SECTION-5": {
                "title": "Famous Leaders of India",
                "difficulty": [DifficultyLevel.JD_JW],
                "topics": [
                    "Mahatma Gandhi - life and principles",
                    "Bhagat Singh - sacrifice and patriotism",
                    "Lal Bahadur Shastri - simplicity and honesty",
                    "Chander Sekhar Azad - revolutionary spirit",
                    "Subash Chandra Bose - leadership and courage",
                    "Swami Vivekanand - spiritual leadership",
                    "Jawaharlal Nehru - modern India's architect",
                    "Maulana Abul Kalam Azad - education and unity",
                    "Sardar Vallabh Bhai Patel - iron man of India"
                ],
                "learning_objectives": [
                    "Knowledge of great leaders",
                    "Understanding their contributions",
                    "Drawing inspiration from their lives"
                ]
            },
            "SECTION-6": {
                "title": "India and Its Neighbours",
                "difficulty": [DifficultyLevel.JD_JW],
                "topics": [
                    "Neighboring countries",
                    "Diplomatic relations",
                    "Cultural connections",
                    "Trade and cooperation"
                ],
                "learning_objectives": [
                    "Knowledge of regional geography",
                    "Understanding international relations",
                    "Awareness of neighborhood policy"
                ]
            },
            "SECTION-7": {
                "title": "Contribution of Youth in National Building",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Role of youth in development",
                    "Youth movements in India",
                    "Social service activities",
                    "Nation building initiatives"
                ],
                "learning_objectives": [
                    "Understanding youth responsibility",
                    "Motivation for social service",
                    "Commitment to nation building"
                ]
            },
            "SECTION-8": {
                "title": "Nation State, National Interests and Objectives",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Concept of nation state",
                    "National interests",
                    "National objectives",
                    "Policy formulation"
                ],
                "learning_objectives": [
                    "Understanding political concepts",
                    "Knowledge of national interests",
                    "Awareness of policy objectives"
                ]
            }
        }
    },
    
    "CHAPTER-III": {
        "title": "FOOT DRILL",
        "wing": Wing.COMMON,
        "sections": {
            "SECTION-1": {
                "title": "General and Words of Command",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Purpose of drill",
                    "Types of commands",
                    "Voice and manner",
                    "Basic positions"
                ],
                "learning_objectives": [
                    "Understanding drill importance",
                    "Proper command execution",
                    "Developing discipline"
                ]
            },
            "SECTION-2": {
                "title": "Attention, Stand at Ease and Stand Easy, Turning and Inclining at the Halt",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Position of attention",
                    "Stand at ease position",
                    "Stand easy position",
                    "Right/left turn",
                    "About turn"
                ],
                "learning_objectives": [
                    "Mastering basic positions",
                    "Proper turning movements",
                    "Developing precision"
                ]
            },
            "SECTION-3": {
                "title": "Sizing, Forming up in Three Ranks, Numbering and Close Order March and Dressing",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Height-wise arrangement",
                    "Three rank formation",
                    "Numbering system",
                    "Dressing and covering"
                ],
                "learning_objectives": [
                    "Understanding formations",
                    "Proper alignment",
                    "Team coordination"
                ]
            },
            "SECTION-4": {
                "title": "Saluting at the Halt, Getting on Parade, Falling Out and Dismissing",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Hand salute technique",
                    "Parade procedures",
                    "Falling out drill",
                    "Dismissal commands"
                ],
                "learning_objectives": [
                    "Proper saluting technique",
                    "Parade discipline",
                    "Ceremonial procedures"
                ]
            },
            "SECTION-5": {
                "title": "Marching: Length of Pace and Time of Marching, Marching in Quick Time and Halt, Slow March and Halt",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Standard pace length",
                    "Marching cadence",
                    "Quick time march",
                    "Slow march",
                    "Halt commands"
                ],
                "learning_objectives": [
                    "Proper marching technique",
                    "Maintaining cadence",
                    "Coordinated movement"
                ]
            },
            "SECTION-6": {
                "title": "Turning at the March and Wheeling",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Turning while marching",
                    "Wheeling movements",
                    "Formation changes",
                    "Pivot techniques"
                ],
                "learning_objectives": [
                    "Advanced marching skills",
                    "Formation coordination",
                    "Precise movements"
                ]
            },
            "SECTION-7": {
                "title": "Saluting at the March",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Saluting while marching",
                    "Eyes right/left",
                    "Ceremonial procedures",
                    "Timing and coordination"
                ],
                "learning_objectives": [
                    "Coordinated saluting",
                    "Ceremonial precision",
                    "Military courtesy"
                ]
            },
            "SECTION-8": {
                "title": "Individual Word of Command",
                "difficulty": [DifficultyLevel.JD_JW],
                "topics": [
                    "Personal drill commands",
                    "Individual movements",
                    "Self-directed drill",
                    "Command execution"
                ],
                "learning_objectives": [
                    "Independent drill execution",
                    "Self-discipline",
                    "Command understanding"
                ]
            },
            "SECTION-9": {
                "title": "Side Pace, Pace Forward and to the Rear",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Side stepping",
                    "Forward pacing",
                    "Rear pacing",
                    "Directional movements"
                ],
                "learning_objectives": [
                    "Advanced movement skills",
                    "Directional control",
                    "Precise positioning"
                ]
            },
            "SECTION-10": {
                "title": "Marking Time, Forward Halt in Quick Time and Changing Step",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Marking time technique",
                    "Forward halt execution",
                    "Step changing",
                    "Rhythm maintenance"
                ],
                "learning_objectives": [
                    "Advanced drill techniques",
                    "Timing precision",
                    "Coordinated movements"
                ]
            },
            "SECTION-11": {
                "title": "Formation of Squad and Squad Drill",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Squad formation",
                    "Squad movements",
                    "Leadership in drill",
                    "Team coordination"
                ],
                "learning_objectives": [
                    "Squad leadership",
                    "Team drill execution",
                    "Formation management"
                ]
            }
        }
    },
    
    "CHAPTER-III(A)": {
        "title": "DRILL WITH ARMS, CEREMONIAL DRILL",
        "wing": Wing.COMMON,
        "difficulty_restriction": [DifficultyLevel.SD_SW],
        "sections": {
            "SECTION-1": {
                "title": "Attention, Stand at Ease and Stand Easy",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Positions with rifle",
                    "Order arms position",
                    "Weapon handling safety",
                    "Basic armed positions"
                ],
                "learning_objectives": [
                    "Safe weapon handling",
                    "Armed drill positions",
                    "Military bearing with arms"
                ]
            },
            "SECTION-2": {
                "title": "Getting on Parade with Rifle and Dressing at the Order",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Parade formation with arms",
                    "Dressing with rifle",
                    "Order arms dressing",
                    "Armed parade procedures"
                ],
                "learning_objectives": [
                    "Armed parade formation",
                    "Weapon coordination",
                    "Ceremonial precision"
                ]
            },
            "SECTION-3": {
                "title": "Dismissing and Falling Out",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Armed dismissal procedures",
                    "Falling out with rifle",
                    "Weapon security",
                    "Safe dispersal"
                ],
                "learning_objectives": [
                    "Safe dismissal procedures",
                    "Weapon accountability",
                    "Disciplined dispersal"
                ]
            },
            "SECTION-4": {
                "title": "Ground and Take up Arms",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Grounding rifle procedure",
                    "Taking up arms",
                    "Weapon placement",
                    "Safety protocols"
                ],
                "learning_objectives": [
                    "Safe weapon handling",
                    "Proper procedures",
                    "Equipment care"
                ]
            },
            "SECTION-5": {
                "title": "Shoulder from the Order and Vice Versa",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Shoulder arms position",
                    "Order to shoulder movement",
                    "Shoulder to order movement",
                    "Smooth transitions"
                ],
                "learning_objectives": [
                    "Weapon position changes",
                    "Smooth execution",
                    "Proper technique"
                ]
            },
            "SECTION-6": {
                "title": "Present from the Order and Vice Versa",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Present arms position",
                    "Order to present movement",
                    "Present to order movement",
                    "Ceremonial presentation"
                ],
                "learning_objectives": [
                    "Ceremonial movements",
                    "Respectful presentation",
                    "Precise execution"
                ]
            },
            "SECTION-7": {
                "title": "Saluting at the Shoulder at the Halt and on the March",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Armed saluting technique",
                    "Saluting while static",
                    "Saluting while marching",
                    "Military courtesy with arms"
                ],
                "learning_objectives": [
                    "Armed saluting skills",
                    "Military courtesy",
                    "Coordinated movements"
                ]
            },
            "SECTION-8": {
                "title": "Short/Long Trail from the Order and Vice Versa",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Trail arms positions",
                    "Short trail technique",
                    "Long trail technique",
                    "Position transitions"
                ],
                "learning_objectives": [
                    "Advanced weapon positions",
                    "Proper technique",
                    "Smooth transitions"
                ]
            },
            "SECTION-9": {
                "title": "Examine Arms",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Weapon inspection procedure",
                    "Examine arms command",
                    "Inspection position",
                    "Safety checks"
                ],
                "learning_objectives": [
                    "Weapon inspection skills",
                    "Safety awareness",
                    "Proper procedures"
                ]
            }
        }
    },
    
    "CHAPTER-IV": {
        "title": "WEAPON TRAINING",
        "wing": Wing.COMMON,
        "sections": {
            "SECTION-1": {
                "title": "Characteristics of .22 Rifle, Stripping, Assembling, Care and Cleaning and Sight Setting",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    ".22 rifle specifications",
                    "Stripping procedure",
                    "Assembly technique",
                    "Cleaning methods",
                    "Sight adjustment"
                ],
                "learning_objectives": [
                    "Weapon knowledge",
                    "Maintenance skills",
                    "Safety practices"
                ]
            },
            "SECTION-2": {
                "title": "Loading/Unloading and Bolt Manipulation",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Loading procedure",
                    "Unloading technique",
                    "Bolt operation",
                    "Safety protocols"
                ],
                "learning_objectives": [
                    "Safe weapon operation",
                    "Proper procedures",
                    "Safety awareness"
                ]
            },
            "SECTION-3": {
                "title": "Lying Position and Hold",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Prone firing position",
                    "Weapon grip",
                    "Body position",
                    "Stability techniques"
                ],
                "learning_objectives": [
                    "Proper firing position",
                    "Accuracy improvement",
                    "Stability control"
                ]
            },
            "SECTION-4": {
                "title": "Aiming I Range and Targets",
                "difficulty": [DifficultyLevel.JD_JW],
                "topics": [
                    "Aiming fundamentals",
                    "Range procedures",
                    "Target types",
                    "Distance estimation"
                ],
                "learning_objectives": [
                    "Basic aiming skills",
                    "Range safety",
                    "Target recognition"
                ]
            },
            "SECTION-5": {
                "title": "Trigger Control and Firing a Shot",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Trigger squeeze technique",
                    "Breathing control",
                    "Shot execution",
                    "Follow through"
                ],
                "learning_objectives": [
                    "Accurate shooting",
                    "Trigger control",
                    "Consistent technique"
                ]
            },
            "SECTION-6": {
                "title": "Range Procedure and Safety Precautions",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Range safety rules",
                    "Command procedures",
                    "Emergency protocols",
                    "Equipment handling"
                ],
                "learning_objectives": [
                    "Safety consciousness",
                    "Range discipline",
                    "Emergency response"
                ]
            },
            "SECTION-7": {
                "title": "Aiming II Alteration of Sight",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Sight adjustment",
                    "Windage correction",
                    "Elevation changes",
                    "Zero confirmation"
                ],
                "learning_objectives": [
                    "Advanced aiming",
                    "Sight adjustment skills",
                    "Precision shooting"
                ]
            },
            "SECTION-8": {
                "title": "Theory of Group and Snap Shooting",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Group shooting theory",
                    "Snap shooting technique",
                    "Quick target engagement",
                    "Accuracy vs speed"
                ],
                "learning_objectives": [
                    "Advanced shooting theory",
                    "Quick engagement skills",
                    "Tactical shooting"
                ]
            },
            "SECTION-9": {
                "title": "Short Range Firing (.22 Rifle), Long/Short Range 7.62mm Rifle Course",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Firing courses",
                    "Range classifications",
                    "Scoring systems",
                    "Qualification standards"
                ],
                "learning_objectives": [
                    "Marksmanship qualification",
                    "Course completion",
                    "Performance standards"
                ]
            },
            "SECTION-10": {
                "title": "Characteristics of 7.62 mm SLR and 5.56 mm INSAS",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "SLR specifications",
                    "INSAS features",
                    "Comparison study",
                    "Operational use"
                ],
                "learning_objectives": [
                    "Weapon knowledge",
                    "Technical understanding",
                    "Comparative analysis"
                ]
            }
        }
    },
    
    "CHAPTER-V": {
        "title": "LEADERSHIP",
        "wing": Wing.COMMON,
        "sections": {
            "SECTION-1": {
                "title": "Motivation",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Nature of motivation",
                    "Types of motivation",
                    "Motivation theories",
                    "Self-motivation techniques"
                ],
                "learning_objectives": [
                    "Understanding motivation",
                    "Self-motivation skills",
                    "Motivating others"
                ]
            },
            "SECTION-2": {
                "title": "Discipline and Duty of a Good Citizen",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Concept of discipline",
                    "Types of discipline",
                    "Civic duties",
                    "Responsible citizenship"
                ],
                "learning_objectives": [
                    "Disciplined behavior",
                    "Civic responsibility",
                    "Good citizenship"
                ]
            },
            "SECTION-3": {
                "title": "Leadership Traits",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Essential leadership qualities",
                    "Character traits",
                    "Behavioral patterns",
                    "Leadership development"
                ],
                "learning_objectives": [
                    "Leadership awareness",
                    "Self-assessment",
                    "Character development"
                ]
            },
            "SECTION-4": {
                "title": "Personality/Character Development",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Personality formation",
                    "Character building",
                    "Self-improvement",
                    "Value system"
                ],
                "learning_objectives": [
                    "Personal growth",
                    "Character building",
                    "Value development"
                ]
            },
            "SECTION-5": {
                "title": "Types of Leadership",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Leadership styles",
                    "Situational leadership",
                    "Democratic vs autocratic",
                    "Transformational leadership"
                ],
                "learning_objectives": [
                    "Leadership styles understanding",
                    "Situational adaptation",
                    "Effective leadership"
                ]
            },
            "SECTION-6": {
                "title": "Values/Code of Ethics",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Moral values",
                    "Ethical principles",
                    "Code of conduct",
                    "Integrity and honesty"
                ],
                "learning_objectives": [
                    "Ethical awareness",
                    "Moral decision making",
                    "Value-based leadership"
                ]
            },
            "SECTION-7": {
                "title": "Perception",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Perceptual process",
                    "Factors affecting perception",
                    "Perceptual errors",
                    "Improving perception"
                ],
                "learning_objectives": [
                    "Understanding perception",
                    "Avoiding biases",
                    "Better judgment"
                ]
            },
            "SECTION-8": {
                "title": "Communication Including Inter-personal Communication",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Communication process",
                    "Verbal and non-verbal communication",
                    "Listening skills",
                    "Interpersonal relations"
                ],
                "learning_objectives": [
                    "Effective communication",
                    "Interpersonal skills",
                    "Better relationships"
                ]
            },
            "SECTION-9": {
                "title": "Effect of Leadership with Historical Examples",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Leadership impact",
                    "Historical leaders",
                    "Leadership lessons",
                    "Case studies"
                ],
                "learning_objectives": [
                    "Leadership appreciation",
                    "Historical awareness",
                    "Learning from examples"
                ]
            },
            "SECTION-10": {
                "title": "Customs of Services",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Military traditions",
                    "Service customs",
                    "Ceremonial practices",
                    "Honor and dignity"
                ],
                "learning_objectives": [
                    "Service appreciation",
                    "Traditional values",
                    "Military etiquette"
                ]
            },
            "SECTION-11": {
                "title": "Importance of Group/Team Work",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Team dynamics",
                    "Group effectiveness",
                    "Cooperation and coordination",
                    "Synergy in teams"
                ],
                "learning_objectives": [
                    "Teamwork skills",
                    "Group leadership",
                    "Collaborative success"
                ]
            }
        }
    },
    
    "CHAPTER-VI": {
        "title": "CIVIL AFFAIRS/DISASTER MANAGEMENT",
        "wing": Wing.COMMON,
        "sections": {
            "SECTION-1": {
                "title": "Civil Defence Organisation and its Duties",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Civil defence structure",
                    "Organizational duties",
                    "Emergency response",
                    "Community protection"
                ],
                "learning_objectives": [
                    "Understanding civil defence",
                    "Emergency preparedness",
                    "Community service"
                ]
            },
            "SECTION-2": {
                "title": "Types of Emergencies/Natural Disasters",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Natural disasters classification",
                    "Man-made emergencies",
                    "Disaster characteristics",
                    "Risk assessment"
                ],
                "learning_objectives": [
                    "Disaster awareness",
                    "Risk recognition",
                    "Emergency preparedness"
                ]
            },
            "SECTION-3": {
                "title": "Fire Fighting",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Fire triangle concept",
                    "Types of fires",
                    "Fire extinguishing methods",
                    "Fire safety measures"
                ],
                "learning_objectives": [
                    "Fire safety knowledge",
                    "Emergency response",
                    "Prevention techniques"
                ]
            },
            "SECTION-4": {
                "title": "Essential Services and their Maintenance",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Public utilities",
                    "Infrastructure maintenance",
                    "Service continuity",
                    "Emergency repairs"
                ],
                "learning_objectives": [
                    "Infrastructure awareness",
                    "Service importance",
                    "Maintenance understanding"
                ]
            },
            "SECTION-5": {
                "title": "Protection",
                "difficulty": [DifficultyLevel.JD_JW],
                "topics": [
                    "Personal protection",
                    "Community safety",
                    "Protective equipment",
                    "Safety protocols"
                ],
                "learning_objectives": [
                    "Safety awareness",
                    "Protection methods",
                    "Risk mitigation"
                ]
            },
            "SECTION-6": {
                "title": "Role of NCC during Natural Hazards",
                "difficulty": [DifficultyLevel.JD_JW],
                "topics": [
                    "NCC disaster response",
                    "Community assistance",
                    "Relief operations",
                    "Coordination with authorities"
                ],
                "learning_objectives": [
                    "Service orientation",
                    "Disaster response",
                    "Community service"
                ]
            },
            "SECTION-7": {
                "title": "Traffic Control during Disaster under Police Supervision",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Traffic management",
                    "Emergency routing",
                    "Coordination with police",
                    "Public safety"
                ],
                "learning_objectives": [
                    "Traffic control skills",
                    "Emergency management",
                    "Authority coordination"
                ]
            },
            "SECTION-8": {
                "title": "Disaster Management during Flood/Cyclone",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Flood response procedures",
                    "Cyclone preparedness",
                    "Evacuation planning",
                    "Relief coordination"
                ],
                "learning_objectives": [
                    "Disaster-specific response",
                    "Emergency planning",
                    "Relief operations"
                ]
            },
            "SECTION-9": {
                "title": "Disaster Management during Earth Quake",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Earthquake preparedness",
                    "Response procedures",
                    "Search and rescue",
                    "Post-earthquake recovery"
                ],
                "learning_objectives": [
                    "Earthquake response",
                    "Rescue techniques",
                    "Recovery planning"
                ]
            },
            "SECTION-10": {
                "title": "Setting up Relief Camp during Disaster Management",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Camp establishment",
                    "Resource management",
                    "Hygiene and sanitation",
                    "Camp administration"
                ],
                "learning_objectives": [
                    "Relief camp management",
                    "Resource coordination",
                    "Administrative skills"
                ]
            },
            "SECTION-11": {
                "title": "Assistance in Removal of Debris",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Debris clearance",
                    "Safety procedures",
                    "Equipment usage",
                    "Coordination with agencies"
                ],
                "learning_objectives": [
                    "Clearance operations",
                    "Safety awareness",
                    "Team coordination"
                ]
            },
            "SECTION-12": {
                "title": "Collection and Distribution of Aid Material",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Aid collection procedures",
                    "Distribution systems",
                    "Inventory management",
                    "Fair distribution"
                ],
                "learning_objectives": [
                    "Relief distribution",
                    "Inventory skills",
                    "Fair allocation"
                ]
            },
            "SECTION-13": {
                "title": "Message Services",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Communication systems",
                    "Message handling",
                    "Emergency communications",
                    "Information dissemination"
                ],
                "learning_objectives": [
                    "Communication skills",
                    "Information management",
                    "Emergency coordination"
                ]
            }
        }
    },
    
    "CHAPTER-VII": {
        "title": "SOCIAL SERVICE",
        "wing": Wing.COMMON,
        "sections": {
            "SECTION-1": {
                "title": "Weaker Sections of our Society and their Needs",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Identification of vulnerable groups",
                    "Socio-economic challenges",
                    "Basic needs assessment",
                    "Support mechanisms"
                ],
                "learning_objectives": [
                    "Social awareness",
                    "Empathy development",
                    "Service orientation"
                ]
            },
            "SECTION-2": {
                "title": "Social Service and its Need",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Importance of social service",
                    "Community development",
                    "Voluntary service",
                    "Social responsibility"
                ],
                "learning_objectives": [
                    "Service motivation",
                    "Social responsibility",
                    "Community engagement"
                ]
            },
            "SECTION-3": {
                "title": "Family Planning",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Population awareness",
                    "Family planning methods",
                    "Health education",
                    "Responsible parenthood"
                ],
                "learning_objectives": [
                    "Population awareness",
                    "Health consciousness",
                    "Responsible behavior"
                ]
            },
            "SECTION-4": {
                "title": "HIV/AIDS: Causes & Prevention and Contribution of Youth Towards Prevention of AIDS",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "HIV/AIDS awareness",
                    "Transmission modes",
                    "Prevention strategies",
                    "Youth role in prevention"
                ],
                "learning_objectives": [
                    "Health awareness",
                    "Prevention knowledge",
                    "Social responsibility"
                ]
            },
            "SECTION-5": {
                "title": "Cancer, its Causes and Preventive Measures",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Cancer types and causes",
                    "Risk factors",
                    "Prevention methods",
                    "Early detection"
                ],
                "learning_objectives": [
                    "Health awareness",
                    "Prevention consciousness",
                    "Healthy lifestyle"
                ]
            },
            "SECTION-6": {
                "title": "Contribution of Youth towards Social Welfare",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Youth power in development",
                    "Social initiatives",
                    "Community programs",
                    "Leadership in service"
                ],
                "learning_objectives": [
                    "Youth empowerment",
                    "Service leadership",
                    "Social impact"
                ]
            },
            "SECTION-7": {
                "title": "NGOs and their Contribution to Society",
                "difficulty": [DifficultyLevel.JD_JW],
                "topics": [
                    "NGO role and functions",
                    "Social development work",
                    "Voluntary organizations",
                    "Community partnerships"
                ],
                "learning_objectives": [
                    "NGO awareness",
                    "Volunteer spirit",
                    "Partnership understanding"
                ]
            },
            "SECTION-8": {
                "title": "Drug Trafficking and Crime",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Drug abuse problems",
                    "Trafficking networks",
                    "Crime prevention",
                    "Youth vulnerability"
                ],
                "learning_objectives": [
                    "Crime awareness",
                    "Prevention knowledge",
                    "Social vigilance"
                ]
            }
        }
    },
    
    "CHAPTER-VIII": {
        "title": "HEALTH AND HYGIENE",
        "wing": Wing.COMMON,
        "sections": {
            "SECTION-1": {
                "title": "Structure and Function of the Human Body",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Body systems overview",
                    "Organ functions",
                    "Physiological processes",
                    "Health maintenance"
                ],
                "learning_objectives": [
                    "Body awareness",
                    "Health understanding",
                    "Physiological knowledge"
                ]
            },
            "SECTION-2": {
                "title": "Hygiene and Sanitation",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Personal hygiene",
                    "Environmental sanitation",
                    "Disease prevention",
                    "Clean habits"
                ],
                "learning_objectives": [
                    "Hygiene consciousness",
                    "Disease prevention",
                    "Healthy practices"
                ]
            },
            "SECTION-3": {
                "title": "Preventable Diseases",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Common preventable diseases",
                    "Vaccination importance",
                    "Prevention strategies",
                    "Public health measures"
                ],
                "learning_objectives": [
                    "Disease awareness",
                    "Prevention knowledge",
                    "Health consciousness"
                ]
            },
            "SECTION-4": {
                "title": "First Aid in Common Medical Emergencies",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Emergency first aid",
                    "Common medical emergencies",
                    "Basic life support",
                    "Emergency response"
                ],
                "learning_objectives": [
                    "First aid skills",
                    "Emergency response",
                    "Life-saving techniques"
                ]
            },
            "SECTION-5": {
                "title": "Dressing of Wounds",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Wound types",
                    "Dressing techniques",
                    "Infection prevention",
                    "Healing process"
                ],
                "learning_objectives": [
                    "Wound care skills",
                    "Infection prevention",
                    "Healing knowledge"
                ]
            },
            "SECTION-6": {
                "title": "Yoga: Introduction and Exercises",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Yoga philosophy",
                    "Basic yoga exercises",
                    "Physical benefits",
                    "Mental wellness"
                ],
                "learning_objectives": [
                    "Yoga awareness",
                    "Physical fitness",
                    "Mental wellness"
                ]
            },
            "SECTION-7": {
                "title": "Physical and Mental Health",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Physical fitness importance",
                    "Mental health awareness",
                    "Stress management",
                    "Holistic wellness"
                ],
                "learning_objectives": [
                    "Holistic health",
                    "Stress management",
                    "Wellness practices"
                ]
            },
            "SECTION-8": {
                "title": "Fractures, Types and Treatment",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Fracture types",
                    "First aid for fractures",
                    "Immobilization techniques",
                    "Emergency care"
                ],
                "learning_objectives": [
                    "Fracture recognition",
                    "Emergency treatment",
                    "Immobilization skills"
                ]
            },
            "SECTION-9": {
                "title": "Evacuation of Casualties",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Casualty evacuation methods",
                    "Transportation techniques",
                    "Safety during evacuation",
                    "Team coordination"
                ],
                "learning_objectives": [
                    "Evacuation techniques",
                    "Safety procedures",
                    "Team coordination"
                ]
            }
        }
    },
    
    "CHAPTER-IX": {
        "title": "ADVENTURE ACTIVITIES",
        "wing": Wing.COMMON,
        "sections": {
            "SECTION-1": {
                "title": "Introduction",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Adventure activities concept",
                    "Benefits and objectives",
                    "Safety considerations",
                    "Character building"
                ],
                "learning_objectives": [
                    "Adventure awareness",
                    "Safety consciousness",
                    "Character development"
                ]
            },
            "SECTION-2": {
                "title": "Trekking",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Trekking basics",
                    "Equipment requirements",
                    "Safety measures",
                    "Navigation skills"
                ],
                "learning_objectives": [
                    "Trekking skills",
                    "Outdoor survival",
                    "Navigation abilities"
                ]
            },
            "SECTION-3": {
                "title": "Cycle Expedition: Planning, Organisation & Conduct",
                "difficulty": [DifficultyLevel.JD_JW],
                "topics": [
                    "Expedition planning",
                    "Route selection",
                    "Equipment preparation",
                    "Safety protocols"
                ],
                "learning_objectives": [
                    "Planning skills",
                    "Organization abilities",
                    "Safety awareness"
                ]
            },
            "SECTION-4": {
                "title": "Para Sailing: Equipment & Conduct",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Para sailing basics",
                    "Equipment knowledge",
                    "Safety procedures",
                    "Weather considerations"
                ],
                "learning_objectives": [
                    "Para sailing awareness",
                    "Equipment knowledge",
                    "Safety protocols"
                ]
            }
        }
    },
    
    "CHAPTER-X": {
        "title": "ENVIRONMENT AND ECOLOGY",
        "wing": Wing.COMMON,
        "sections": {
            "SECTION-1": {
                "title": "What is Environment",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Environmental components",
                    "Natural and artificial environment",
                    "Environmental systems",
                    "Human-environment interaction"
                ],
                "learning_objectives": [
                    "Environmental awareness",
                    "System understanding",
                    "Interaction knowledge"
                ]
            },
            "SECTION-2": {
                "title": "What is Ecology",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Ecological concepts",
                    "Ecosystem components",
                    "Food chains and webs",
                    "Ecological balance"
                ],
                "learning_objectives": [
                    "Ecological understanding",
                    "Balance awareness",
                    "System knowledge"
                ]
            },
            "SECTION-3": {
                "title": "Conservation of Environment and Ecology",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Conservation importance",
                    "Conservation methods",
                    "Sustainable practices",
                    "Individual responsibility"
                ],
                "learning_objectives": [
                    "Conservation awareness",
                    "Sustainable practices",
                    "Environmental responsibility"
                ]
            },
            "SECTION-4": {
                "title": "Pollution and its Control",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Types of pollution",
                    "Pollution sources",
                    "Control measures",
                    "Prevention strategies"
                ],
                "learning_objectives": [
                    "Pollution awareness",
                    "Control knowledge",
                    "Prevention skills"
                ]
            },
            "SECTION-5": {
                "title": "Forest Ecology and Pollution",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Forest ecosystems",
                    "Forest importance",
                    "Deforestation effects",
                    "Forest conservation"
                ],
                "learning_objectives": [
                    "Forest awareness",
                    "Conservation importance",
                    "Environmental impact"
                ]
            },
            "SECTION-6": {
                "title": "Wild Life",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Wildlife importance",
                    "Biodiversity concepts",
                    "Wildlife conservation",
                    "Endangered species"
                ],
                "learning_objectives": [
                    "Wildlife awareness",
                    "Conservation consciousness",
                    "Biodiversity appreciation"
                ]
            }
        }
    },
    
    "CHAPTER-XI": {
        "title": "SELF DEFENCE",
        "wing": Wing.COMMON,
        "sections": {
            "SECTION-1": {
                "title": "Precaution and General Behavior of Boys/Girls Cadets",
                "difficulty": [DifficultyLevel.JD_JW],
                "topics": [
                    "Safety precautions",
                    "Behavioral guidelines",
                    "Risk awareness",
                    "Personal safety"
                ],
                "learning_objectives": [
                    "Safety consciousness",
                    "Risk awareness",
                    "Preventive behavior"
                ]
            },
            "SECTION-2": {
                "title": "Prevention of Untoward Incidents",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Incident prevention",
                    "Situational awareness",
                    "Risk mitigation",
                    "Safety strategies"
                ],
                "learning_objectives": [
                    "Prevention skills",
                    "Awareness development",
                    "Safety planning"
                ]
            },
            "SECTION-3": {
                "title": "Vulnerable Parts of the Body",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Body vulnerability points",
                    "Protection methods",
                    "Self-defense awareness",
                    "Safety techniques"
                ],
                "learning_objectives": [
                    "Body awareness",
                    "Protection knowledge",
                    "Defense understanding"
                ]
            },
            "SECTION-4": {
                "title": "Physical Self Defence",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Basic self-defense techniques",
                    "Escape methods",
                    "Physical defense skills",
                    "Emergency response"
                ],
                "learning_objectives": [
                    "Self-defense skills",
                    "Physical preparedness",
                    "Emergency response"
                ]
            }
        }
    },
    
    "CHAPTER-XII": {
        "title": "POSTURE TRAINING",
        "wing": Wing.COMMON,
        "difficulty_restriction": [DifficultyLevel.SD_SW],
        "sections": {
            "SECTION-1": {
                "title": "Aim and Principles of Posture Training and its Importance",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Posture training objectives",
                    "Training principles",
                    "Health importance",
                    "Physical development"
                ],
                "learning_objectives": [
                    "Posture awareness",
                    "Health consciousness",
                    "Physical development"
                ]
            },
            "SECTION-2": {
                "title": "Anatomy and Relationship of Body Segments",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Body segment anatomy",
                    "Skeletal system",
                    "Muscular system",
                    "Postural relationships"
                ],
                "learning_objectives": [
                    "Anatomical knowledge",
                    "Body awareness",
                    "Structural understanding"
                ]
            },
            "SECTION-3": {
                "title": "Analysis of Good Posture",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Good posture characteristics",
                    "Postural alignment",
                    "Balance and stability",
                    "Health benefits"
                ],
                "learning_objectives": [
                    "Posture analysis",
                    "Good posture recognition",
                    "Health awareness"
                ]
            },
            "SECTION-4": {
                "title": "Causes of Bad Posture Remedial and Preventive Measure",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Bad posture causes",
                    "Remedial exercises",
                    "Prevention strategies",
                    "Corrective measures"
                ],
                "learning_objectives": [
                    "Problem identification",
                    "Corrective knowledge",
                    "Prevention skills"
                ]
            },
            "SECTION-5": {
                "title": "Balanced Alignment and Exercise",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Body alignment principles",
                    "Balance exercises",
                    "Alignment correction",
                    "Exercise routines"
                ],
                "learning_objectives": [
                    "Alignment skills",
                    "Balance development",
                    "Exercise knowledge"
                ]
            },
            "SECTION-6": {
                "title": "Balanced Diet",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Nutrition importance",
                    "Balanced diet components",
                    "Dietary guidelines",
                    "Health maintenance"
                ],
                "learning_objectives": [
                    "Nutritional awareness",
                    "Diet planning",
                    "Health consciousness"
                ]
            },
            "SECTION-7": {
                "title": "Correct Standing and Exercises",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Correct standing posture",
                    "Standing exercises",
                    "Postural correction",
                    "Strength building"
                ],
                "learning_objectives": [
                    "Standing posture skills",
                    "Exercise techniques",
                    "Postural improvement"
                ]
            },
            "SECTION-8": {
                "title": "Correct Walking and Exercises",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Proper walking technique",
                    "Gait analysis",
                    "Walking exercises",
                    "Movement efficiency"
                ],
                "learning_objectives": [
                    "Walking skills",
                    "Movement efficiency",
                    "Exercise application"
                ]
            },
            "SECTION-9": {
                "title": "Correct Use of Body in Motion",
                "difficulty": [DifficultyLevel.SD_SW],
                "topics": [
                    "Body mechanics",
                    "Movement principles",
                    "Efficient motion",
                    "Injury prevention"
                ],
                "learning_objectives": [
                    "Movement efficiency",
                    "Body mechanics",
                    "Injury prevention"
                ]
            }
        }
    },
    
    "CHAPTER-XIII": {
        "title": "MISCELLANEOUS",
        "wing": Wing.COMMON,
        "sections": {
            "SECTION-1": {
                "title": "Career Options in Services: Army, Navy & Air Force",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Military career paths",
                    "Service branches overview",
                    "Entry requirements",
                    "Career progression"
                ],
                "learning_objectives": [
                    "Career awareness",
                    "Service knowledge",
                    "Career planning"
                ]
            },
            "SECTION-2": {
                "title": "Selection Process: WTLOs",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Selection procedures",
                    "WTLO process",
                    "Preparation strategies",
                    "Assessment criteria"
                ],
                "learning_objectives": [
                    "Selection awareness",
                    "Preparation knowledge",
                    "Process understanding"
                ]
            },
            "SECTION-3": {
                "title": "Traffic Rules and Road Signs",
                "difficulty": [DifficultyLevel.JD_JW, DifficultyLevel.SD_SW],
                "topics": [
                    "Traffic regulations",
                    "Road sign meanings",
                    "Traffic safety",
                    "Responsible driving"
                ],
                "learning_objectives": [
                    "Traffic awareness",
                    "Safety consciousness",
                    "Responsible behavior"
                ]
            }
        }
    }
}

# Utility functions for syllabus management
def get_chapters_by_difficulty(difficulty: DifficultyLevel) -> Dict:
    """Get all chapters available for a specific difficulty level"""
    filtered_chapters = {}
    for chapter_id, chapter_data in NCC_SYLLABUS.items():
        chapter_sections = {}
        for section_id, section_data in chapter_data["sections"].items():
            if difficulty in section_data["difficulty"]:
                chapter_sections[section_id] = section_data
        if chapter_sections:
            filtered_chapters[chapter_id] = {
                **chapter_data,
                "sections": chapter_sections
            }
    return filtered_chapters

def get_sections_by_chapter(chapter_id: str, difficulty: DifficultyLevel = None) -> Dict:
    """Get all sections for a specific chapter, optionally filtered by difficulty"""
    if chapter_id not in NCC_SYLLABUS:
        return {}
    
    chapter = NCC_SYLLABUS[chapter_id]
    if difficulty is None:
        return chapter["sections"]
    
    filtered_sections = {}
    for section_id, section_data in chapter["sections"].items():
        if difficulty in section_data["difficulty"]:
            filtered_sections[section_id] = section_data
    
    return filtered_sections

def get_topics_by_section(chapter_id: str, section_id: str) -> List[str]:
    """Get all topics for a specific section"""
    try:
        return NCC_SYLLABUS[chapter_id]["sections"][section_id]["topics"]
    except KeyError:
        return []

def get_learning_objectives(chapter_id: str, section_id: str) -> List[str]:
    """Get learning objectives for a specific section"""
    try:
        return NCC_SYLLABUS[chapter_id]["sections"][section_id]["learning_objectives"]
    except KeyError:
        return []

def get_all_topics_for_difficulty(difficulty: DifficultyLevel) -> List[Tuple[str, str, str, str]]:
    """Get all topics for a difficulty level as (chapter_id, chapter_title, section_id, topic)"""
    topics = []
    for chapter_id, chapter_data in NCC_SYLLABUS.items():
        for section_id, section_data in chapter_data["sections"].items():
            if difficulty in section_data["difficulty"]:
                for topic in section_data["topics"]:
                    topics.append((
                        chapter_id,
                        chapter_data["title"],
                        section_id,
                        topic
                    ))
    return topics

def search_topics(keyword: str, difficulty: DifficultyLevel = None) -> List[Dict]:
    """Search for topics containing a keyword"""
    results = []
    for chapter_id, chapter_data in NCC_SYLLABUS.items():
        for section_id, section_data in chapter_data["sections"].items():
            # Check difficulty filter
            if difficulty and difficulty not in section_data["difficulty"]:
                continue
                
            # Search in topics
            for topic in section_data["topics"]:
                if keyword.lower() in topic.lower():
                    results.append({
                        "chapter_id": chapter_id,
                        "chapter_title": chapter_data["title"],
                        "section_id": section_id,
                        "section_title": section_data["title"],
                        "topic": topic,
                        "difficulty": section_data["difficulty"]
                    })
    return results

# Question difficulty mapping based on Bloom's Taxonomy
QUESTION_DIFFICULTY_MAPPING = {
    DifficultyLevel.JD_JW: {
        "remember": 0.4,      # 40% - Basic recall
        "understand": 0.3,    # 30% - Comprehension
        "apply": 0.2,         # 20% - Application
        "analyze": 0.1,       # 10% - Analysis
        "evaluate": 0.0,      # 0% - Too advanced
        "create": 0.0         # 0% - Too advanced
    },
    DifficultyLevel.SD_SW: {
        "remember": 0.2,      # 20% - Basic recall
        "understand": 0.25,   # 25% - Comprehension
        "apply": 0.25,        # 25% - Application
        "analyze": 0.2,       # 20% - Analysis
        "evaluate": 0.1,
        "create": 0.0         # 0% - Too advanced
    }
}
