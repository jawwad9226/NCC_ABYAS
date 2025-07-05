"""
Gamification System for NCC ABYAS
Provides badges, achievements, leaderboards, and engagement features
"""
import streamlit as st
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict

class BadgeSystem:
    """Badge and achievement system"""
    
    BADGES = {
        # Learning Badges
        "first_steps": {
            "name": "First Steps",
            "description": "Welcome to NCC ABYAS! Complete your first activity.",
            "icon": "👶",
            "color": "#4CAF50",
            "category": "getting_started",
            "requirements": {
                "type": "activity_count",
                "count": 1
            }
        },
        "quick_learner": {
            "name": "Quick Learner",
            "description": "Complete 5 activities in one day",
            "icon": "⚡",
            "color": "#FF9800",
            "category": "speed",
            "requirements": {
                "type": "daily_activities",
                "count": 5
            }
        },
        "dedicated_cadet": {
            "name": "Dedicated Cadet",
            "description": "Use the app for 7 consecutive days",
            "icon": "🎖️",
            "color": "#2196F3",
            "category": "consistency",
            "requirements": {
                "type": "consecutive_days",
                "count": 7
            }
        },
        "knowledge_seeker": {
            "name": "Knowledge Seeker",
            "description": "Ask 50 questions in chat",
            "icon": "🤔",
            "color": "#9C27B0",
            "category": "engagement",
            "requirements": {
                "type": "chat_messages",
                "count": 50
            }
        },
        
        # Quiz Badges
        "quiz_rookie": {
            "name": "Quiz Rookie",
            "description": "Complete your first quiz",
            "icon": "🏁",
            "color": "#4CAF50",
            "category": "quiz",
            "requirements": {
                "type": "quiz_count",
                "count": 1
            }
        },
        "perfectionist": {
            "name": "Perfectionist",
            "description": "Score 100% on a quiz",
            "icon": "💯",
            "color": "#FFD700",
            "category": "quiz",
            "requirements": {
                "type": "perfect_score",
                "count": 1
            }
        },
        "quiz_master": {
            "name": "Quiz Master",
            "description": "Complete 25 quizzes",
            "icon": "👑",
            "color": "#FF6B6B",
            "category": "quiz",
            "requirements": {
                "type": "quiz_count",
                "count": 25
            }
        },
        "streak_warrior": {
            "name": "Streak Warrior",
            "description": "Achieve a 10-quiz winning streak",
            "icon": "🔥",
            "color": "#FF5722",
            "category": "quiz",
            "requirements": {
                "type": "quiz_streak",
                "count": 10
            }
        },
        
        # Knowledge Badges
        "drill_expert": {
            "name": "Drill Expert",
            "description": "Excel in drill-related questions",
            "icon": "🎯",
            "color": "#607D8B",
            "category": "knowledge",
            "requirements": {
                "type": "topic_expertise",
                "topic": "drill",
                "accuracy": 90,
                "questions": 20
            }
        },
        "leadership_scholar": {
            "name": "Leadership Scholar",
            "description": "Master leadership principles",
            "icon": "👨‍💼",
            "color": "#795548",
            "category": "knowledge",
            "requirements": {
                "type": "topic_expertise",
                "topic": "leadership",
                "accuracy": 90,
                "questions": 20
            }
        },
        
        # Special Badges
        "early_bird": {
            "name": "Early Bird",
            "description": "Complete activities before 8 AM",
            "icon": "🌅",
            "color": "#FFEB3B",
            "category": "special",
            "requirements": {
                "type": "early_activity",
                "count": 5
            }
        },
        "night_owl": {
            "name": "Night Owl",
            "description": "Study after 10 PM",
            "icon": "🦉",
            "color": "#3F51B5",
            "category": "special",
            "requirements": {
                "type": "late_activity",
                "count": 5
            }
        },
        "social_learner": {
            "name": "Social Learner",
            "description": "Provide feedback 5 times",
            "icon": "💬",
            "color": "#E91E63",
            "category": "community",
            "requirements": {
                "type": "feedback_count",
                "count": 5
            }
        }
    }
    
    @staticmethod
    def check_earned_badges(user_stats: Dict[str, Any]) -> List[str]:
        """Check which badges the user has earned"""
        earned_badges = []
        
        for badge_id, badge in BadgeSystem.BADGES.items():
            if BadgeSystem._meets_requirements(badge["requirements"], user_stats):
                earned_badges.append(badge_id)
        
        return earned_badges
    
    @staticmethod
    def _meets_requirements(requirements: Dict[str, Any], user_stats: Dict[str, Any]) -> bool:
        """Check if user meets badge requirements"""
        req_type = requirements["type"]
        
        if req_type == "activity_count":
            total_activities = (
                user_stats.get("quiz_count", 0) + 
                user_stats.get("chat_count", 0) +
                user_stats.get("video_views", 0)
            )
            return total_activities >= requirements["count"]
        
        elif req_type == "quiz_count":
            return user_stats.get("quiz_count", 0) >= requirements["count"]
        
        elif req_type == "perfect_score":
            return user_stats.get("perfect_scores", 0) >= requirements["count"]
        
        elif req_type == "quiz_streak":
            return user_stats.get("best_streak", 0) >= requirements["count"]
        
        elif req_type == "chat_messages":
            return user_stats.get("chat_count", 0) >= requirements["count"]
        
        elif req_type == "consecutive_days":
            return user_stats.get("consecutive_days", 0) >= requirements["count"]
        
        elif req_type == "daily_activities":
            return user_stats.get("max_daily_activities", 0) >= requirements["count"]
        
        elif req_type == "topic_expertise":
            topic_stats = user_stats.get("topic_performance", {}).get(requirements["topic"], {})
            accuracy = topic_stats.get("accuracy", 0)
            questions = topic_stats.get("questions_answered", 0)
            return accuracy >= requirements["accuracy"] and questions >= requirements["questions"]
        
        elif req_type == "feedback_count":
            return user_stats.get("feedback_given", 0) >= requirements["count"]
        
        elif req_type == "early_activity":
            return user_stats.get("early_activities", 0) >= requirements["count"]
        
        elif req_type == "late_activity":
            return user_stats.get("late_activities", 0) >= requirements["count"]
        
        return False

class LevelSystem:
    """Experience points and level system"""
    
    # XP values for different activities
    XP_VALUES = {
        "chat_message": 5,
        "quiz_completed": 50,
        "quiz_perfect": 100,
        "daily_login": 10,
        "streak_bonus": 25,
        "video_watched": 15,
        "feedback_given": 20,
        "syllabus_viewed": 10
    }
    
    # Level thresholds
    LEVEL_THRESHOLDS = [
        0, 100, 250, 500, 1000, 1750, 2750, 4000, 5500, 7500, 10000,
        13000, 16500, 20500, 25000, 30000, 35500, 41500, 48000, 55000, 62500
    ]
    
    LEVEL_TITLES = [
        "NCC Recruit", "Cadet", "Experienced Cadet", "Senior Cadet", "Junior Leader",
        "Squad Leader", "Platoon Leader", "Company Leader", "Battalion Leader", "Regiment Leader",
        "Brigade Leader", "Division Leader", "Corps Leader", "Army Commander", "Field Marshal",
        "NCC Legend", "Grand Master", "Supreme Commander", "Ultimate Leader", "NCC Champion",
        "Eternal Guardian"
    ]
    
    @staticmethod
    def calculate_level_and_xp(total_xp: int) -> Dict[str, Any]:
        """Calculate current level, progress, and next level requirements"""
        current_level = 0
        
        for i, threshold in enumerate(LevelSystem.LEVEL_THRESHOLDS):
            if total_xp >= threshold:
                current_level = i
            else:
                break
        
        # Calculate progress to next level
        if current_level < len(LevelSystem.LEVEL_THRESHOLDS) - 1:
            current_threshold = LevelSystem.LEVEL_THRESHOLDS[current_level]
            next_threshold = LevelSystem.LEVEL_THRESHOLDS[current_level + 1]
            progress_xp = total_xp - current_threshold
            needed_xp = next_threshold - current_threshold
            progress_percentage = (progress_xp / needed_xp) * 100
            xp_to_next = next_threshold - total_xp
        else:
            progress_percentage = 100
            xp_to_next = 0
        
        title = LevelSystem.LEVEL_TITLES[min(current_level, len(LevelSystem.LEVEL_TITLES) - 1)]
        
        return {
            "level": current_level,
            "title": title,
            "total_xp": total_xp,
            "progress_percentage": progress_percentage,
            "xp_to_next": xp_to_next
        }

class EngagementTracker:
    """Track user engagement and activity patterns"""
    
    @staticmethod
    def record_activity(activity_type: str, details: Dict[str, Any] = None):
        """Record a user activity"""
        if "activity_log" not in st.session_state:
            st.session_state.activity_log = []
        
        activity = {
            "type": activity_type,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        st.session_state.activity_log.append(activity)
        
        # Award XP
        xp_earned = LevelSystem.XP_VALUES.get(activity_type, 0)
        if xp_earned > 0:
            if "total_xp" not in st.session_state:
                st.session_state.total_xp = 0
            st.session_state.total_xp += xp_earned
    
    @staticmethod
    def get_user_stats() -> Dict[str, Any]:
        """Calculate comprehensive user statistics"""
        activity_log = st.session_state.get("activity_log", [])
        quiz_history = st.session_state.get("quiz_ss_quiz_score_history", [])
        chat_messages = st.session_state.get("messages", [])
        
        stats = {
            "total_xp": st.session_state.get("total_xp", 0),
            "quiz_count": len(quiz_history),
            "chat_count": len([msg for msg in chat_messages if msg.get("role") == "user"]),
            "perfect_scores": 0,
            "best_streak": 0,
            "consecutive_days": 0,
            "max_daily_activities": 0,
            "early_activities": 0,
            "late_activities": 0,
            "feedback_given": 0,
            "video_views": 0,
            "topic_performance": {}
        }
        
        # Calculate quiz-specific stats
        if quiz_history:
            perfect_scores = sum(1 for quiz in quiz_history 
                               if quiz.get("score", 0) == quiz.get("total_questions", 0))
            stats["perfect_scores"] = perfect_scores
            
            # Calculate best streak
            current_streak = 0
            best_streak = 0
            for quiz in reversed(quiz_history):
                accuracy = (quiz.get("score", 0) / max(quiz.get("total_questions", 1), 1)) * 100
                if accuracy >= 70:
                    current_streak += 1
                    best_streak = max(best_streak, current_streak)
                else:
                    current_streak = 0
            stats["best_streak"] = best_streak
        
        # Calculate activity patterns
        activity_by_date = defaultdict(int)
        for activity in activity_log:
            try:
                date = datetime.fromisoformat(activity["timestamp"]).date()
                activity_by_date[date] += 1
                
                # Check time patterns
                time = datetime.fromisoformat(activity["timestamp"]).time()
                if time.hour < 8:
                    stats["early_activities"] += 1
                elif time.hour >= 22:
                    stats["late_activities"] += 1
                    
            except:
                continue
        
        if activity_by_date:
            stats["max_daily_activities"] = max(activity_by_date.values())
        
        # Calculate consecutive days
        if activity_by_date:
            sorted_dates = sorted(activity_by_date.keys(), reverse=True)
            consecutive_days = 0
            current_date = datetime.now().date()
            
            for date in sorted_dates:
                if date == current_date or (current_date - date).days == consecutive_days + 1:
                    consecutive_days += 1
                    current_date = date
                else:
                    break
            
            stats["consecutive_days"] = consecutive_days
        
        return stats

def show_gamification_dashboard():
    """Display the gamification dashboard"""
    st.markdown("### 🎮 Your Progress & Achievements")
    
    # Get user stats
    user_stats = EngagementTracker.get_user_stats()
    
    # Level and XP display
    level_info = LevelSystem.calculate_level_and_xp(user_stats["total_xp"])
    
    # Level progress card
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        text-align: center;
    ">
        <h2 style="margin: 0; color: white;">🏆 {level_info['title']}</h2>
        <div style="font-size: 1.2rem; margin: 0.5rem 0;">Level {level_info['level']}</div>
        <div style="background: rgba(255,255,255,0.2); border-radius: 10px; padding: 0.5rem; margin: 1rem 0;">
            <div style="background: linear-gradient(90deg, #4CAF50, #8BC34A); height: 10px; border-radius: 5px; width: {level_info['progress_percentage']}%;"></div>
        </div>
        <div style="font-size: 0.9rem; opacity: 0.9;">
            {user_stats['total_xp']} XP | {level_info['xp_to_next']} XP to next level
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🧠 Quizzes", user_stats["quiz_count"])
    with col2:
        st.metric("💬 Chat Messages", user_stats["chat_count"])
    with col3:
        st.metric("🔥 Best Streak", user_stats["best_streak"])
    with col4:
        st.metric("📅 Active Days", user_stats["consecutive_days"])
    
    # Badges section
    st.markdown("#### 🏅 Badges & Achievements")
    
    earned_badge_ids = BadgeSystem.check_earned_badges(user_stats)
    earned_badges = [BadgeSystem.BADGES[badge_id] for badge_id in earned_badge_ids]
    
    if earned_badges:
        # Group badges by category
        badge_categories = defaultdict(list)
        for badge in earned_badges:
            badge_categories[badge["category"]].append(badge)
        
        for category, badges in badge_categories.items():
            st.markdown(f"**{category.replace('_', ' ').title()}**")
            
            cols = st.columns(min(len(badges), 4))
            for i, badge in enumerate(badges):
                with cols[i % 4]:
                    st.markdown(f"""
                    <div style="
                        background: {badge['color']};
                        color: white;
                        padding: 1rem;
                        border-radius: 0.5rem;
                        text-align: center;
                        margin: 0.5rem 0;
                    ">
                        <div style="font-size: 2rem;">{badge['icon']}</div>
                        <div style="font-weight: bold; font-size: 0.9rem;">{badge['name']}</div>
                        <div style="font-size: 0.8rem; opacity: 0.9;">{badge['description']}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("🎯 Start using the app to earn your first badges!")
    
    # Progress towards next badges
    st.markdown("#### 🎯 Next Goals")
    
    all_badges = BadgeSystem.BADGES
    unearned_badges = [
        (badge_id, badge) for badge_id, badge in all_badges.items() 
        if badge_id not in earned_badge_ids
    ]
    
    if unearned_badges:
        # Show a few next achievable badges
        next_badges = unearned_badges[:6]  # Show first 6 unearned badges
        
        cols = st.columns(3)
        for i, (badge_id, badge) in enumerate(next_badges):
            with cols[i % 3]:
                # Calculate progress towards this badge
                progress = _calculate_badge_progress(badge["requirements"], user_stats)
                
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    padding: 1rem;
                    border-radius: 0.5rem;
                    text-align: center;
                    margin: 0.5rem 0;
                    border: 2px dashed {badge['color']};
                ">
                    <div style="font-size: 1.5rem; opacity: 0.7;">{badge['icon']}</div>
                    <div style="font-weight: bold; font-size: 0.9rem; color: #333;">{badge['name']}</div>
                    <div style="font-size: 0.8rem; color: #666; margin: 0.5rem 0;">{badge['description']}</div>
                    <div style="background: #ddd; border-radius: 10px; height: 6px; margin: 0.5rem 0;">
                        <div style="background: {badge['color']}; height: 6px; border-radius: 10px; width: {progress}%;"></div>
                    </div>
                    <div style="font-size: 0.7rem; color: #888;">{progress:.0f}% complete</div>
                </div>
                """, unsafe_allow_html=True)

def _calculate_badge_progress(requirements: Dict[str, Any], user_stats: Dict[str, Any]) -> float:
    """Calculate progress percentage towards a badge"""
    req_type = requirements["type"]
    
    if req_type == "activity_count":
        total_activities = (
            user_stats.get("quiz_count", 0) + 
            user_stats.get("chat_count", 0) +
            user_stats.get("video_views", 0)
        )
        return min(100, (total_activities / requirements["count"]) * 100)
    
    elif req_type == "quiz_count":
        return min(100, (user_stats.get("quiz_count", 0) / requirements["count"]) * 100)
    
    elif req_type == "chat_messages":
        return min(100, (user_stats.get("chat_count", 0) / requirements["count"]) * 100)
    
    elif req_type == "consecutive_days":
        return min(100, (user_stats.get("consecutive_days", 0) / requirements["count"]) * 100)
    
    elif req_type == "quiz_streak":
        return min(100, (user_stats.get("best_streak", 0) / requirements["count"]) * 100)
    
    # Add more progress calculations as needed
    return 0

def award_xp(activity_type: str, details: Dict[str, Any] = None, custom_xp: int = None):
    """Award XP for an activity (convenience function)"""
    if custom_xp:
        if "total_xp" not in st.session_state:
            st.session_state.total_xp = 0
        st.session_state.total_xp += custom_xp
    
    EngagementTracker.record_activity(activity_type, details)

def show_xp_notification(xp_amount: int, reason: str):
    """Show XP earned notification"""
    st.success(f"🎉 +{xp_amount} XP earned for {reason}!")
