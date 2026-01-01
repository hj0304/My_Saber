# analysis/models.py
from django.db import models

class MlbPlayerCost(models.Model):
    PLAYER_TYPES = (
        ('batter', '타자'),
        ('pitcher', '투수'),
    )

    id = models.AutoField(primary_key=True)
    year = models.IntegerField(db_index=True)      # 연도 (2020 ~ 2025)
    name = models.CharField(max_length=100, db_index=True) # 선수명
    team = models.CharField(max_length=50)         # 팀명
    player_type = models.CharField(max_length=10, choices=PLAYER_TYPES, default='batter') # 타자/투수 구분
    
    # 데이터
    salary = models.BigIntegerField(default=0)     # 연봉 (AAV) - 단위: 달러
    war = models.FloatField(default=0.0)           # WAR
    dollars = models.BigIntegerField(default=0)    # 가치 환산 금액 (Dollars) - 단위: 달러 (DB에는 정수로 저장)
    
    # 계산된 지표
    surplus_value = models.BigIntegerField(default=0) # 잉여 가치 (Dollars - Salary)

    class Meta:
        indexes = [
            models.Index(fields=['year', 'player_type']),
            models.Index(fields=['year', 'name']),
        ]
        unique_together = ('year', 'name', 'player_type') # 중복 방지

    def __str__(self):
        return f"{self.year} {self.name} ({self.player_type})"