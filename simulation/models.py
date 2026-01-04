# simulation/models.py
from django.db import models

class PitchData(models.Model):
    # 검색 및 필터링을 위한 핵심 필드
    player_name = models.CharField(max_length=100, db_index=True)
    game_date = models.DateField(null=True, blank=True)
    p_throws = models.CharField(max_length=10, null=True, blank=True)
    pitch_type = models.CharField(max_length=10, null=True, blank=True)
    
    # 투구 추적 데이터 (Physics)
    release_speed = models.FloatField(null=True, blank=True)
    release_pos_x = models.FloatField(null=True, blank=True)
    release_pos_y = models.FloatField(null=True, blank=True)
    release_pos_z = models.FloatField(null=True, blank=True)
    
    vx0 = models.FloatField(null=True, blank=True)
    vy0 = models.FloatField(null=True, blank=True)
    vz0 = models.FloatField(null=True, blank=True)
    ax = models.FloatField(null=True, blank=True)
    ay = models.FloatField(null=True, blank=True)
    az = models.FloatField(null=True, blank=True)
    
    sz_top = models.FloatField(null=True, blank=True)
    sz_bot = models.FloatField(null=True, blank=True)
    
    pfx_x = models.FloatField(null=True, blank=True)
    pfx_z = models.FloatField(null=True, blank=True)
    
    release_spin_rate = models.FloatField(null=True, blank=True)
    
    plate_x = models.FloatField(null=True, blank=True)
    plate_z = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.player_name} - {self.pitch_type}"