"""
Quiz Analytics Module for NCC ABYAS
Provides comprehensive analytics, performance tracking, and gamification features for the quiz system
"""
import streamlit as st
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict, Counter

class QuizAnalytics:
    """Comprehensive quiz analytics and performance tracking"""
    
    @staticmethod
    def calculate_performance_metrics(quiz_history: List[Dict]) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        if not quiz_history:
            return {
                "total_quizzes": 0,
                "average_score": 0,
                "total_questions_answered": 0,
                "accuracy_rate": 0,
                "improvement_trend": "No data",
                "streak_current": 0,
                "streak_best": 0,
                "time_spent_total": 0,
                "average_time_per_question": 0,
                "difficulty_performance": {},
                "topic_performance": {},
                "recent_performance": "No data"
            }
        
        # Basic metrics
        total_quizzes = len(quiz_history)
        total_questions = sum(entry.get('total_questions', 0) for entry in quiz_history)
        total_correct = sum(entry.get('score', 0) for entry in quiz_history)
        total_time = sum(entry.get('time_taken', 0) for entry in quiz_history)
        
        average_score = (total_correct / total_questions * 100) if total_questions > 0 else 0
        accuracy_rate = average_score
        average_time_per_question = (total_time / total_questions) if total_questions > 0 else 0
        
        # Streak calculation
        current_streak = 0
        best_streak = 0
        temp_streak = 0
        
        for entry in reversed(quiz_history):  # Start from most recent
            score_percentage = (entry.get('score', 0) / max(entry.get('total_questions', 1), 1)) * 100
            if score_percentage >= 70:  # 70% threshold for success
                temp_streak += 1
                if current_streak == 0:  # Still counting current streak
                    current_streak = temp_streak
            else:
                if current_streak == 0:  # Current streak broken
                    current_streak = 0
                best_streak = max(best_streak, temp_streak)
                temp_streak = 0
        
        best_streak = max(best_streak, temp_streak)
        
        # Improvement trend
        if len(quiz_history) >= 3:
            recent_scores = [
                (entry.get('score', 0) / max(entry.get('total_questions', 1), 1)) * 100 
                for entry in quiz_history[-3:]
            ]
            if recent_scores[-1] > recent_scores[0]:
                improvement_trend = "Improving"
            elif recent_scores[-1] < recent_scores[0]:
                improvement_trend = "Declining"
            else:
                improvement_trend = "Stable"
        else:
            improvement_trend = "Insufficient data"
        
        # Difficulty performance
        difficulty_performance = QuizAnalytics._analyze_difficulty_performance(quiz_history)
        
        # Topic performance
        topic_performance = QuizAnalytics._analyze_topic_performance(quiz_history)
        
        # Recent performance (last 7 days)
        recent_performance = QuizAnalytics._analyze_recent_performance(quiz_history)
        
        return {
            "total_quizzes": total_quizzes,
            "average_score": round(average_score, 1),
            "total_questions_answered": total_questions,
            "accuracy_rate": round(accuracy_rate, 1),
            "improvement_trend": improvement_trend,
            "streak_current": current_streak,
            "streak_best": best_streak,
            "time_spent_total": round(total_time / 3600, 1),  # Convert to hours
            "average_time_per_question": round(average_time_per_question, 1),
            "difficulty_performance": difficulty_performance,
            "topic_performance": topic_performance,
            "recent_performance": recent_performance
        }
    
    @staticmethod
    def _analyze_difficulty_performance(quiz_history: List[Dict]) -> Dict[str, Dict]:
        """Analyze performance by difficulty level"""
        difficulty_stats = defaultdict(lambda: {"total": 0, "correct": 0, "time": 0})
        
        for entry in quiz_history:
            difficulty = entry.get('difficulty', 'Medium')
            difficulty_stats[difficulty]["total"] += entry.get('total_questions', 0)
            difficulty_stats[difficulty]["correct"] += entry.get('score', 0)
            difficulty_stats[difficulty]["time"] += entry.get('time_taken', 0)
        
        performance = {}
        for difficulty, stats in difficulty_stats.items():
            if stats["total"] > 0:
                accuracy = (stats["correct"] / stats["total"]) * 100
                avg_time = stats["time"] / stats["total"]
                performance[difficulty] = {
                    "accuracy": round(accuracy, 1),
                    "questions_answered": stats["total"],
                    "average_time": round(avg_time, 1)
                }
        
        return performance
    
    @staticmethod
    def _analyze_topic_performance(quiz_history: List[Dict]) -> Dict[str, Dict]:
        """Analyze performance by topic/category"""
        # This would need to be enhanced based on how topics are tracked
        # For now, return basic analysis
        topic_stats = defaultdict(lambda: {"total": 0, "correct": 0})
        
        for entry in quiz_history:
            # If topics are stored in the entry
            topics = entry.get('topics', ['General NCC'])
            if isinstance(topics, str):
                topics = [topics]
            
            questions_per_topic = entry.get('total_questions', 0) / len(topics)
            score_per_topic = entry.get('score', 0) / len(topics)
            
            for topic in topics:
                topic_stats[topic]["total"] += questions_per_topic
                topic_stats[topic]["correct"] += score_per_topic
        
        performance = {}
        for topic, stats in topic_stats.items():
            if stats["total"] > 0:
                accuracy = (stats["correct"] / stats["total"]) * 100
                performance[topic] = {
                    "accuracy": round(accuracy, 1),
                    "questions_answered": int(stats["total"])
                }
        
        return performance
    
    @staticmethod
    def _analyze_recent_performance(quiz_history: List[Dict]) -> str:
        """Analyze recent performance trend"""
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        
        recent_quizzes = []
        for entry in quiz_history:
            try:
                quiz_date = datetime.strptime(entry.get('timestamp', ''), '%Y-%m-%d %H:%M:%S')
                if quiz_date >= week_ago:
                    recent_quizzes.append(entry)
            except:
                continue
        
        if not recent_quizzes:
            return "No recent activity"
        
        recent_accuracy = sum(
            (entry.get('score', 0) / max(entry.get('total_questions', 1), 1)) * 100 
            for entry in recent_quizzes
        ) / len(recent_quizzes)
        
        if recent_accuracy >= 80:
            return f"Excellent ({len(recent_quizzes)} quizzes, {recent_accuracy:.1f}% avg)"
        elif recent_accuracy >= 60:
            return f"Good ({len(recent_quizzes)} quizzes, {recent_accuracy:.1f}% avg)"
        else:
            return f"Needs improvement ({len(recent_quizzes)} quizzes, {recent_accuracy:.1f}% avg)"

class GamificationSystem:
    """Gamification features for quiz engagement"""
    
    ACHIEVEMENTS = {
        "first_quiz": {
            "name": "Getting Started",
            "description": "Complete your first quiz",
            "icon": "🎯",
            "requirement": lambda stats: stats["total_quizzes"] >= 1
        },
        "perfect_score": {
            "name": "Perfect Score",
            "description": "Get 100% on any quiz",
            "icon": "🎯",
            "requirement": lambda stats: any(
                entry.get('score', 0) == entry.get('total_questions', 0) 
                for entry in st.session_state.get('quiz_ss_quiz_score_history', [])
            )
        },
        "quiz_master": {
            "name": "Quiz Master",
            "description": "Complete 10 quizzes",
            "icon": "👑",
            "requirement": lambda stats: stats["total_quizzes"] >= 10
        },
        "streak_5": {
            "name": "Hot Streak",
            "description": "5 quiz winning streak",
            "icon": "🔥",
            "requirement": lambda stats: stats["streak_best"] >= 5
        },
        "speed_demon": {
            "name": "Speed Demon",
            "description": "Average less than 30 seconds per question",
            "icon": "⚡",
            "requirement": lambda stats: stats["average_time_per_question"] < 30
        },
        "scholar": {
            "name": "NCC Scholar",
            "description": "Answer 100 questions correctly",
            "icon": "📚",
            "requirement": lambda stats: sum(
                entry.get('score', 0) 
                for entry in st.session_state.get('quiz_ss_quiz_score_history', [])
            ) >= 100
        }
    }
    
    @staticmethod
    def check_achievements(stats: Dict[str, Any]) -> List[Dict[str, str]]:
        """Check which achievements have been unlocked"""
        unlocked = []
        
        for achievement_id, achievement in GamificationSystem.ACHIEVEMENTS.items():
            if achievement["requirement"](stats):
                unlocked.append({
                    "id": achievement_id,
                    "name": achievement["name"],
                    "description": achievement["description"],
                    "icon": achievement["icon"]
                })
        
        return unlocked
    
    @staticmethod
    def get_next_achievements(stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get next achievements to work towards"""
        next_achievements = []
        
        # Logic to suggest next achievements based on current progress
        if stats["total_quizzes"] < 10:
            next_achievements.append({
                "name": "Quiz Master",
                "description": f"Complete {10 - stats['total_quizzes']} more quizzes",
                "icon": "👑",
                "progress": (stats["total_quizzes"] / 10) * 100
            })
        
        if stats["streak_best"] < 5:
            next_achievements.append({
                "name": "Hot Streak",
                "description": f"Build a {5 - stats['streak_current']} quiz winning streak",
                "icon": "🔥",
                "progress": (stats["streak_current"] / 5) * 100
            })
        
        return next_achievements

def show_quiz_analytics_dashboard():
    """Display comprehensive quiz analytics dashboard"""
    st.markdown("### 📊 Quiz Performance Analytics")
    
    # Get quiz history
    quiz_history = st.session_state.get('quiz_ss_quiz_score_history', [])
    
    if not quiz_history:
        st.info("📈 Complete some quizzes to see your analytics dashboard!")
        return
    
    # Calculate metrics
    metrics = QuizAnalytics.calculate_performance_metrics(quiz_history)
    
    # Performance overview
    st.markdown("#### 🎯 Performance Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Overall Accuracy", 
            f"{metrics['accuracy_rate']}%",
            delta=f"{metrics['improvement_trend']}"
        )
    
    with col2:
        st.metric(
            "Quizzes Completed", 
            metrics['total_quizzes'],
            delta=f"{metrics['total_questions_answered']} questions"
        )
    
    with col3:
        st.metric(
            "Current Streak", 
            metrics['streak_current'],
            delta=f"Best: {metrics['streak_best']}"
        )
    
    with col4:
        st.metric(
            "Study Time", 
            f"{metrics['time_spent_total']}h",
            delta=f"{metrics['average_time_per_question']}s/question"
        )
    
    # Performance charts
    if len(quiz_history) > 1:
        st.markdown("#### 📈 Performance Trends")
        
        # Prepare data for charts
        dates = []
        scores = []
        
        for entry in quiz_history:
            try:
                date = datetime.strptime(entry.get('timestamp', ''), '%Y-%m-%d %H:%M:%S')
                dates.append(date)
                accuracy = (entry.get('score', 0) / max(entry.get('total_questions', 1), 1)) * 100
                scores.append(accuracy)
            except:
                continue
        
        if dates and scores:
            # Create performance trend chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=scores,
                mode='lines+markers',
                name='Quiz Accuracy',
                line=dict(color='#667eea', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title="Quiz Performance Over Time",
                xaxis_title="Date",
                yaxis_title="Accuracy (%)",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Difficulty analysis
    if metrics['difficulty_performance']:
        st.markdown("#### 🎚️ Performance by Difficulty")
        
        difficulty_data = []
        for difficulty, perf in metrics['difficulty_performance'].items():
            difficulty_data.append({
                'Difficulty': difficulty,
                'Accuracy': perf['accuracy'],
                'Questions': perf['questions_answered']
            })
        
        df_difficulty = pd.DataFrame(difficulty_data)
        
        fig = px.bar(
            df_difficulty, 
            x='Difficulty', 
            y='Accuracy',
            title='Accuracy by Difficulty Level',
            color='Accuracy',
            color_continuous_scale='RdYlGn'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Achievements
    st.markdown("#### 🏆 Achievements")
    
    achievements = GamificationSystem.check_achievements(metrics)
    
    if achievements:
        cols = st.columns(min(len(achievements), 3))
        for i, achievement in enumerate(achievements):
            with cols[i % 3]:
                st.success(f"{achievement['icon']} **{achievement['name']}**\n\n{achievement['description']}")
    
    # Next achievements
    next_achievements = GamificationSystem.get_next_achievements(metrics)
    if next_achievements:
        st.markdown("#### 🎯 Goals to Work Towards")
        for achievement in next_achievements:
            progress = achievement.get('progress', 0)
            st.markdown(f"**{achievement['icon']} {achievement['name']}**")
            st.progress(progress / 100)
            st.caption(achievement['description'])

def show_detailed_quiz_history():
    """Show detailed quiz history with filtering and search"""
    st.markdown("### 📚 Detailed Quiz History")
    
    quiz_history = st.session_state.get('quiz_ss_quiz_score_history', [])
    
    if not quiz_history:
        st.info("📝 No quiz history available yet. Complete some quizzes to see your detailed history!")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Date filter
        date_filter = st.selectbox(
            "Time Period",
            ["All Time", "Last 7 days", "Last 30 days", "Last 90 days"]
        )
    
    with col2:
        # Difficulty filter
        difficulties = list(set(entry.get('difficulty', 'Medium') for entry in quiz_history))
        difficulty_filter = st.selectbox("Difficulty", ["All"] + difficulties)
    
    with col3:
        # Score filter
        score_filter = st.selectbox(
            "Performance",
            ["All", "Excellent (80%+)", "Good (60-79%)", "Needs Improvement (<60%)"]
        )
    
    # Filter data
    filtered_history = quiz_history.copy()
    
    # Apply date filter
    if date_filter != "All Time":
        days = {"Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90}[date_filter]
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_history = [
            entry for entry in filtered_history
            if datetime.strptime(entry.get('timestamp', ''), '%Y-%m-%d %H:%M:%S') >= cutoff_date
        ]
    
    # Apply difficulty filter
    if difficulty_filter != "All":
        filtered_history = [
            entry for entry in filtered_history
            if entry.get('difficulty', 'Medium') == difficulty_filter
        ]
    
    # Apply score filter
    if score_filter != "All":
        for entry in filtered_history:
            accuracy = (entry.get('score', 0) / max(entry.get('total_questions', 1), 1)) * 100
            if score_filter == "Excellent (80%+)" and accuracy < 80:
                filtered_history.remove(entry)
            elif score_filter == "Good (60-79%)" and (accuracy < 60 or accuracy >= 80):
                filtered_history.remove(entry)
            elif score_filter == "Needs Improvement (<60%)" and accuracy >= 60:
                filtered_history.remove(entry)
    
    st.markdown(f"**Showing {len(filtered_history)} of {len(quiz_history)} quizzes**")
    
    # Display filtered history
    for i, entry in enumerate(reversed(filtered_history)):
        timestamp = entry.get('timestamp', 'Unknown')
        score = entry.get('score', 0)
        total = entry.get('total_questions', 0)
        accuracy = (score / max(total, 1)) * 100
        difficulty = entry.get('difficulty', 'Medium')
        time_taken = entry.get('time_taken', 0)
        
        # Color based on performance
        if accuracy >= 80:
            color = "🟢"
        elif accuracy >= 60:
            color = "🟡"
        else:
            color = "🔴"
        
        with st.expander(f"{color} Quiz #{len(quiz_history) - i} - {timestamp} - {accuracy:.1f}%"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Score", f"{score}/{total}")
            with col2:
                st.metric("Accuracy", f"{accuracy:.1f}%")
            with col3:
                st.metric("Difficulty", difficulty)
            with col4:
                st.metric("Time", f"{time_taken:.0f}s")
            
            # Show questions if available
            questions = entry.get('questions', [])
            if questions:
                st.markdown("**Questions:**")
                for j, q in enumerate(questions, 1):
                    user_answer = q.get('user_answer', 'Not answered')
                    correct_answer = q.get('correct_answer', 'Unknown')
                    is_correct = q.get('is_correct', False)
                    
                    status = "✅" if is_correct else "❌"
                    st.markdown(f"{status} **Q{j}:** {q.get('question', 'Question not available')}")
                    st.markdown(f"   Your answer: {user_answer}")
                    if not is_correct:
                        st.markdown(f"   Correct answer: {correct_answer}")

def create_quiz_performance_summary():
    """Create a compact performance summary widget"""
    quiz_history = st.session_state.get('quiz_ss_quiz_score_history', [])
    
    if not quiz_history:
        return
    
    metrics = QuizAnalytics.calculate_performance_metrics(quiz_history)
    
    # Create a compact summary card
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 1rem;
        margin: 1rem 0;
        text-align: center;
    ">
        <h3 style="margin: 0; color: white;">📊 Your Quiz Performance</h3>
        <div style="display: flex; justify-content: space-around; margin-top: 1rem;">
            <div>
                <div style="font-size: 1.5rem; font-weight: bold;">{metrics['accuracy_rate']}%</div>
                <div style="font-size: 0.8rem; opacity: 0.9;">Accuracy</div>
            </div>
            <div>
                <div style="font-size: 1.5rem; font-weight: bold;">{metrics['total_quizzes']}</div>
                <div style="font-size: 0.8rem; opacity: 0.9;">Quizzes</div>
            </div>
            <div>
                <div style="font-size: 1.5rem; font-weight: bold;">{metrics['streak_current']}</div>
                <div style="font-size: 0.8rem; opacity: 0.9;">Streak</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
