import pyrebase
import json


class DBhandler:
    def __init__(self):
        with open('./authentication/firebase_auth.json') as f:
            config = json.load(f)
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()
        
    # ===== 1) 맛집 data =====

    # DB에 저장
    def insert_restaurant(self, name, data, img_path):
        restaurant_info ={
            "store_phoneNum": data['store_phoneNum'],
            "store_addr": data['store_addr'],
            "store_site": data['store_site'],
            "store_open": data['store_open'],
            "store_close": data['store_close'],
            "store_parking": data['store_parking'],
            "store_reservation": data['store_reservation'],
            "store_reservation_link": data['store_reservation_link'],
            "store_category": data['store_category'],
            "store_cost_min": data['store_cost_min'],
            "store_cost_max": data['store_cost_max'],
            "img_path": img_path,
            "store_grade": 0,
            "store_taste": 0,
            "store_cost": 0,
            "store_service": 0,
            "store_cleanliness": 0,
            "store_atmosphere": 0,
            "store_revisit": 0,
            "store_reviewCount": 0
        }
        # self.db.child("restaurant").child(name).set(restaurant_info)
        # return True
        if self.restaurant_duplicate_check(name):
           self.db.child("restaurant").child(name).child("info").set(restaurant_info)
           print(data, img_path)
           return True
        else:
            return False

    # 맛집 등록 시 중복 체크
    def restaurant_duplicate_check(self, name):
        restaurants = self.db.child("restaurant").get()
        if restaurants.each() == None:
            return True
        for res in restaurants.each():
            if res.key() == name:
                return False
        return True

    # DB 데이터 읽어오기
    def get_restaurants(self):
        restaurants = self.db.child("restaurant").get().val()
        return restaurants

    # 가게 이름으로 특정 가게 정보 가져오기
    def get_restaurant_byname(self, name):
        restaurants = self.db.child("restaurant").get()
        target_value = ""
        for res in restaurants.each():
            value=res.val()
            if res.key() == name:
                target_value=value
        return target_value
    
    
    def get_reviews_byname(self,name):
        reviews = self.db.child("restaurant").child(name).child("review").get().val()
        return reviews
    
    #가게별 리뷰 개수 구하기    
    def get_reviewcount_byname(self,name):
        reviews = self.db.child("restaurant").child(name).child("review").get().val()
        return len(reviews)
    
    #리뷰에 접근하여 가게 평점 계산하기
    def get_avgrate_byname(self,name):
        reviews = self.db.child("restaurant").child(name).child("review").get()
        review_grades=[]
        for rev in reviews.each():
            value = rev.val()
            review_grades.append(float(value['review_grade']))
        result = sum(review_grades)/len(review_grades)
        result = round(result, 1)
        return result
    
    #리뷰에 접근하여 가게 재방문의사 계산하기
    def get_revisitrate_byname(self,name):
        reviews = self.db.child("restaurant").child(name).child("review").get()
        reviews_cnt=self.get_reviewcount_byname(name)
        revisit_count=0
        for rev in reviews.each():
            value = rev.val()
            if(value['revisit']=='y'):
                revisit_count+=1
        return int(revisit_count/reviews_cnt*100)
    
    #다섯가지 키워드 응답자 수 계산
    def review_keyword_respondent_check(self, name):
        reviews = self.db.child("restaurant").child(name).child("review").get()
        respondent=0
        for rev in reviews.each():
            value = rev.val()
            if((value['taste']=='y') or (value['cost']=='y') or (value['service']=='y') or (value['cleanliness']=='y') or (value['atmosphere']=='y')): #하나라도 y이면 응답자로 생각
                respondent+=1
                continue
        return respondent
    
    # 리뷰에 접근하여 다섯가지 키워드 별 계산하기-taste
    def get_tasteScore_byname(self, name):
        reviews = self.db.child("restaurant").child(name).child("review").get()
        respondent = self.review_keyword_respondent_check(name)
        taste_count = 0
        for rev in reviews.each():
            value = rev.val()
            if (value['taste'] == 'y'):
                taste_count += 1
        return int(taste_count/respondent*100)
    
    #리뷰에 접근하여 다섯가지 키워드 별 계산하기-cost
    def get_costScore_byname(self,name):
        reviews = self.db.child("restaurant").child(name).child("review").get()
        respondent=self.review_keyword_respondent_check(name)
        cost_count=0
        for rev in reviews.each():
            value = rev.val()
            if(value['taste']=='y'):
                cost_count+=1
        return int(cost_count/respondent*100)
    
    #리뷰에 접근하여 다섯가지 키워드 별 계산하기-service
    def get_serviceScore_byname(self,name):
        reviews = self.db.child("restaurant").child(name).child("review").get()
        respondent=self.review_keyword_respondent_check(name)
        service_count=0
        for rev in reviews.each():
            value = rev.val()
            if(value['service']=='y'):
                service_count+=1
        return int(service_count/respondent*100)
    
     # 리뷰에 접근하여 다섯가지 키워드 별 계산하기-cleanliness
    def get_cleanlinessScore_byname(self, name):
        reviews = self.db.child("restaurant").child(name).child("review").get()
        respondent = self.review_keyword_respondent_check(name)
        cleanliness_count = 0
        for rev in reviews.each():
            value = rev.val()
            if (value['cleanliness'] == 'y'):
                cleanliness_count += 1
        return int(cleanliness_count/respondent*100)

    # 리뷰에 접근하여 다섯가지 키워드 별 계산하기-atmosphere
    def get_atmosphereScore_byname(self, name):
        reviews = self.db.child("restaurant").child(name).child("review").get()
        respondent = self.review_keyword_respondent_check(name)
        atmosphere_count = 0
        for rev in reviews.each():
            value = rev.val()
            if (value['atmosphere'] == 'y'):
                atmosphere_count += 1
        return int(atmosphere_count/respondent*100)
    
        

    # ===== 2) 메뉴 data ======

    def insert_menu(self, name, data, menuImg_path):
        menu_info = {
            "menuImg_path": menuImg_path,
            "menu_name": data['menu_name'],
            "menu_price": data['menu_price'],
            "extra_ve": data['extra_ve'],
            "extra_al": data['extra_al']
        }
        # self.db.child("restaurant").child(name).child("menu").child('menu_name').set(menu_info)
        # return True
        if self.menu_duplicate_check(data['menu_name']):
            self.db.child("restaurant").child(name).child(
                "menu").child(data['menu_name']).set(menu_info)
            print(data, menuImg_path)
            return True
        else:
            return False

    def menu_duplicate_check(self, name):
        menus = self.db.child("restaurant").child(name).child("menu").get()
        if menus.each() == None:
            return True
        for res in menus.each():
            if res.key() == name:
                return False
        return True
    
      # 가게 이름으로 특정 가게 메뉴 가져오기
    def get_menu_byname(self, name):
        menus = self.db.child("restaurant").child(name).child("menu").get()
        target_value=[]
        for menu in menus.each():
            value = menu.val()
            target_value.append(value)
        return target_value
    
    # ===== 3) 리뷰 데이터 ======
    def insert_review(self, name, data, reviewImg_path):
        review_info = {
            "store_name": name,
            "nickname": data['nickname'],
            "review_grade": data['Range'],
            "taste": data['taste'],
            "cost": data['cost'],
            "service": data['service'],
            "cleanliness": data['cleanliness'],
            "atmosphere": data['atmosphere'],
            "revisit": data['revisit'],
            "detail_review": data['detail_review'],
            "reviewImg_path": reviewImg_path
        }
        if data['nickname'] == "":
            review_info['nickname'] = "익명"
        self.db.child("restaurant").child(name).child("review").push(review_info)
        self.update_storeScore_byname(name)
    
    def get_review_byname(self, name):
        reviews = self.db.child("restaurant").child(name).child("review").get()
        target_value=[]
        # value = reviews.val()
        # target_value.append(value)  
        for rev in reviews.each():
            value = rev.val()
            target_value.append(value)
        return target_value

        
    #리뷰 등록할 때마다 평점(평점, 재방문의사, 키워드5)을 업데이트
    def update_storeScore_byname(self, name):
        avgScore = self.get_avgrate_byname(name)
        tasteScore = self.get_tasteScore_byname(name)
        costScore = self.get_costScore_byname(name)
        serviceScore = self.get_serviceScore_byname(name)
        cleanlinessScore = self.get_cleanlinessScore_byname(name)
        atmosphereScore = self.get_atmosphereScore_byname(name)
        revisit = self.get_revisitrate_byname(name)
        self.db.child("restaurant").child(name).child("info").update({"store_grade":avgScore})
        self.db.child("restaurant").child(name).child("info").update({"store_taste":tasteScore})
        self.db.child("restaurant").child(name).child("info").update({"store_cost":costScore})
        self.db.child("restaurant").child(name).child("info").update({"store_service":serviceScore})
        self.db.child("restaurant").child(name).child("info").update({"store_cleanliness":cleanlinessScore})
        self.db.child("restaurant").child(name).child("info").update({"store_atmosphere":atmosphereScore})
        self.db.child("restaurant").child(name).child("info").update({"store_revisit":revisit})
        

    # 회원 가입 화면
    def insert_member(self, name, data):  # 회원 가입 페이지
        member_info = {
            "memberInfo_password": data['memberInfo_password'],
            "memberInfo_rePassword": data['memberInfo_rePassword'],
            "memberInfo_birthDate": data['memberInfo_birthDate'],
            "memberInfo_sex": data['memberInfo_sex']
        }
        if self.id_duplicate_check(name):
            if data['memberInfo_password'] == data['memberInfo_rePassword']:
                self.db.child("member").child(name).set(member_info)
                return True
            else:
                return False

    def id_duplicate_check(self, name):
        members = self.db.child("member").get()
        if members.each() == None:
            return True
        for res in members.each():
            if res.key() == name:
                return False
        return True
