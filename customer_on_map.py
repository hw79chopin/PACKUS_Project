korea = [36.39, 127.28]
map_korea = folium.Map(location=korea, zoom_start=7)

# 군집 0
cluster_0 = data[data['군집_5']==0]
# 군집 1
cluster_1 = data[data['군집_5']==1]
# 군집 2
cluster_2 = data[data['군집_5']==2]
# 군집 3
cluster_3 = data[data['군집_5']==3]
# 군집 4
cluster_4 = data[data['군집_5']==4]

# 군집 0 찍기
for customer in tqdm(list(cluster_0['주문자ID'].unique())):
    temp = cluster_0[cluster_0['주문자ID']==customer]
    folium.Marker([temp['위도'].values[0], temp['경도'].values[0]], popup=customer, icon=folium.Icon(icon='cloud', color = "black")).add_to(map_korea)

# 군집 1 찍기
for customer in tqdm(list(cluster_1['주문자ID'].unique())):
    temp = cluster_1[cluster_1['주문자ID']==customer]
    folium.Marker([temp['위도'].values[0], temp['경도'].values[0]], popup=customer, icon=folium.Icon(icon='cloud', color = "green")).add_to(map_korea)
    
# 군집 2 찍기
for customer in tqdm(list(cluster_2['주문자ID'].unique())):
    temp = cluster_2[cluster_2['주문자ID']==customer]
    folium.Marker([temp['위도'].values[0], temp['경도'].values[0]], popup=customer, icon=folium.Icon(icon='cloud', color = "purple")).add_to(map_korea)
    
# 군집 3 찍기
for customer in tqdm(list(cluster_3['주문자ID'].unique())):
    temp = cluster_3[cluster_3['주문자ID']==customer]
    folium.Marker([temp['위도'].values[0], temp['경도'].values[0]], popup=customer, icon=folium.Icon(icon='cloud', color = 'blue')).add_to(map_korea)
    
# 군집 4 찍기
for customer in tqdm(list(cluster_4['주문자ID'].unique())):
    temp = cluster_4[cluster_4['주문자ID']==customer]
    folium.Marker([temp['위도'].values[0], temp['경도'].values[0]], popup=customer, icon=folium.Icon(icon='cloud', color = "red")).add_to(map_korea)    

map_korea.save('지도시각화_프렌즈 등급 이상.html')