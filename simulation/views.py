# simulation/views.py
from django.shortcuts import render
import pandas as pd
import json
import os
from django.conf import settings
# 모든 시즌 + 대용량을 위한
from .models import PitchData
from django.db.models import Max
import random

def pitch_tunnel_view(request):
    # 1. 검색어 확인
    query_pitcher = request.GET.get('pitcher')
    
    target_pitcher_name = ""
    pitch_data = []

    # 2. 투수 선정 로직
    if query_pitcher:
        # 검색어가 있으면 해당 투수 이름 찾기 (가장 비슷한 이름 1명)
        # icontains로 검색 후, 첫 번째 결과의 정확한 이름을 가져옴
        found = PitchData.objects.filter(player_name__icontains=query_pitcher).first()
        if found:
            target_pitcher_name = found.player_name
    else:
        # 검색어가 없으면(초기 접속) -> 랜덤 투수 선정
        # DB에서 무작위 데이터 하나를 찍어서 그 선수의 이름을 가져옴 (속도 최적화)
        max_id = PitchData.objects.aggregate(max_id=Max("id"))['max_id']
        if max_id:
            while not target_pitcher_name:
                pk = random.randint(1, max_id)
                random_pitch = PitchData.objects.filter(pk=pk).first()
                if random_pitch:
                    target_pitcher_name = random_pitch.player_name

    # 3. 데이터 조회 (선정된 투수의 데이터 가져오기)
    if target_pitcher_name:
        queryset = PitchData.objects.filter(player_name=target_pitcher_name)
        
        # 데이터가 너무 많으면 최신순 300개 -> 랜덤 섞기
        count = queryset.count()
        limit = 300
        
        if count > limit:
            # 최신 500개 중 300개 랜덤 샘플링 (다양성 확보)
            data_list = list(queryset.values().order_by('-game_date')[:500])
            pitch_data = random.sample(data_list, limit)
        else:
            pitch_data = list(queryset.values())
            
    else:
        # DB가 비어있거나 검색 결과가 없는 경우
        print("No pitcher found.")
        target_pitcher_name = "Not Found"

    context = {
        'pitch_data': json.dumps(pitch_data, default=str), # 날짜 등 직렬화
        'target_pitcher': target_pitcher_name
    }
    
    return render(request, 'simulation/pitch_tunnel.html', context)