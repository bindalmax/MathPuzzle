"""
Gap Detector Service
Uses pandas and numpy to identify learning gaps and calculate severity scores.
"""

import pandas as pd
import numpy as np
from database import db, ProblemAttempt
from flask import current_app

class GapDetector:
    @staticmethod
    def detect_learning_gaps(user_name, min_attempts=5):
        """
        Identify topics where the user's accuracy is below 70%.
        
        Returns:
            list: Sorted list of (category, success_rate) tuples.
        """
        # Fetch all attempts for the user
        attempts = ProblemAttempt.query.filter_by(user_name=user_name).all()
        
        if not attempts:
            return []
            
        # Convert to DataFrame for easier aggregation
        data = [
            {'category': a.category, 'is_correct': a.is_correct}
            for a in attempts
        ]
        df = pd.DataFrame(data)
        
        # Calculate success rate and count per category
        stats = df.groupby('category')['is_correct'].agg(['mean', 'count'])
        
        # Filter by minimum attempts and success threshold (70%)
        gaps = stats[(stats['count'] >= min_attempts) & (stats['mean'] < 0.7)]
        
        # Convert to dictionary and calculate severity
        gap_list = []
        for category, row in gaps.iterrows():
            severity = GapDetector.calculate_severity_score(row['mean'], row['count'])
            gap_list.append({
                'category': category,
                'success_rate': round(row['mean'], 3),
                'attempts': int(row['count']),
                'severity_score': severity
            })
            
        # Sort by severity (highest first)
        return sorted(gap_list, key=lambda x: x['severity_score'], reverse=True)

    @staticmethod
    def calculate_severity_score(success_rate, attempts_count):
        """
        Calculate severity based on accuracy and confidence (number of attempts).
        """
        confidence = min(attempts_count / 20, 1.0)
        severity = (1 - success_rate) * confidence
        return round(severity, 2)
