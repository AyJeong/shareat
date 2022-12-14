import pyrebase
import json
from datetime import datetime


class DBhandler:
    def __init__(self):
        with open('./authentication/firebase_auth.json') as f:
            config = json.load(f)
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

    # ===== 1) 맛집 data =====

    # DB에 저장
    def insert_restaurant(self, name, data, img_paths):
        # 맛집 등록 시간 DB에 저장
        now = datetime.now()
        str_year = now.strftime("%Y")
        str_month = now.strftime("%m")
        str_day = now.strftime("%d")
        str_hour = now.strftime("%H")
        str_minute = now.strftime("%M")
        str_second = now.strftime("%S")
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

        restaurant_time = {
            "str_year": str_year,
            "str_month": str_month,
            "str_day": str_day,
            "str_hour": str_hour,
            "str_minute": str_minute,
            "str_second": str_second,
            "timestamp": timestamp,
        }
        # 맛집 정보를 DB에 저장
        restaurant_info = {
            "store_name": data['store_name'],
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
            "store_grade": 0,
            "store_taste": 0,
            "store_cost": 0,
            "store_service": 0,
            "store_cleanliness": 0,
            "store_atmosphere": 0,
            "store_revisit": 0,
            "store_reviewCount": 0,
            "main_image" : img_paths[0],
            "img_path": ""
            
        }
        #가게이름 중복체크 후 데이터 삽입.
        if self.restaurant_duplicate_check(name):
            self.db.child("restaurant").child(name).child("info").set(restaurant_info)
            self.db.child("restaurant").child(name).child("time").set(restaurant_time)
            for path in img_paths:
                self.db.child("restaurant").child(name).child("info").child("img_path").push(path)
            return True
        else:
            return False
    
    # DB에 수정
    def modify_restaurant(self, name, data, img_paths):
        # 맛집 등록 시간 DB에 저장
        now = datetime.now()
        str_year = now.strftime("%Y")
        str_month = now.strftime("%m")
        str_day = now.strftime("%d")
        str_hour = now.strftime("%H")
        str_minute = now.strftime("%M")
        str_second = now.strftime("%S")
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

        restaurant_time = {
            "str_year": str_year,
            "str_month": str_month,
            "str_day": str_day,
            "str_hour": str_hour,
            "str_minute": str_minute,
            "str_second": str_second,
            "timestamp": timestamp,
        }
        # 맛집 정보를 DB에 저장
        restaurant_info = {
            "store_name": data['store_name'],
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
            "main_image" : img_paths[0],
            "img_path": ""
        }
        # self.db.child("restaurant").child(name).set(restaurant_info)
        # return True
        if self.restaurant_duplicate_check(name):
            return False
        else:
            self.db.child("restaurant").child(name).child("info").update(restaurant_info)
            self.db.child("restaurant").child(name).child("time").update(restaurant_time)
            for path in img_paths:
                self.db.child("restaurant").child(name).child("info").child("img_path").push(path)
            return True

    # 맛집 등록 시 중복 체크
    def restaurant_duplicate_check(self, name):
        restaurants = self.db.child("restaurant").get()
        if restaurants.each() == None:
            return True
        for res in restaurants.each():
            if res.key() == name:
                return False
        return True

    # DB 데이터 가져오기
    def get_restaurants(self):
        restaurants = self.db.child("restaurant").get().val()
        return restaurants

    # 카테고리로 맛집 목록 가져오기
    def get_restaurants_bycategory(self, cate):
        retaurants = self.db.child("restaurant").get()
        target_value = []
        for res in retaurants.each():
            value = res.val()

            if value['info']['store_category'] == cate:
                target_value.append(value)

        new_dict = {}
        for k, v in enumerate(target_value):
            new_dict[k] = v

        return new_dict

    # 가게 이름으로 특정 가게 정보 가져오기
    def get_restaurant_byname(self, name):
        restaurants = self.db.child("restaurant").get()
        target_value = ""
        for res in restaurants.each():
            value = res.val()
            if res.key() == name:
                target_value = value
        return target_value
    
    # 가게 이름으로 가게 이미지 가져오기
    def get_restaurant_imgs_byname(self, name):
        imgs = self.db.child("restaurant").child(name).child("info").child("img_path").get()
        img_paths=[]
        if imgs.each() == None:
            return img_paths
        for img in imgs.each():
            img_paths.append(img.val())
        return img_paths

    # 리뷰 목록 가져오기
    def get_reviews_byname(self, name):
        reviews = self.db.child("restaurant").child(
            name).child("review").get().val()
        return reviews

    # 가게별 리뷰 개수 구하기
    def get_reviewcount_byname(self, name):
        reviews = self.db.child("restaurant").child(
            name).child("review").get().val()
        return len(reviews)

    # 리뷰에 접근하여 가게 평점 계산하기
    def get_avgrate_byname(self, name):
        reviews = self.db.child("restaurant").child(name).child("review").get()
        review_grades = []
        for rev in reviews.each():
            value = rev.val()
            review_grades.append(float(value['review_grade']))
        result = sum(review_grades)/len(review_grades)
        result = round(result, 1)
        return result

    # 리뷰에 접근하여 가게 재방문의사 계산하기
    def get_revisitrate_byname(self, name):
        reviews = self.db.child("restaurant").child(name).child("review").get()
        reviews_cnt = self.get_reviewcount_byname(name)
        revisit_count = 0
        for rev in reviews.each():
            value = rev.val()
            if (value['revisit'] == 'y'):
                revisit_count += 1
        return int(revisit_count/reviews_cnt*100)

    # 다섯가지 키워드 응답자 수 계산 !주의! 0일 경우 internal 에러라니까 조건문 추가해야함.
    def review_keyword_respondent_check(self, name):
        reviews = self.db.child("restaurant").child(name).child("review").get()
        respondent = 0
        for rev in reviews.each():
            value = rev.val()
            if ((value['taste'] == 'y') or (value['cost'] == 'y') or (value['service'] == 'y') or (value['cleanliness'] == 'y') or (value['atmosphere'] == 'y')):  # 하나라도 y이면 응답자로 생각
                respondent += 1
                continue
        return respondent

    # 리뷰에 접근하여 다섯가지 키워드 별 계산하기-taste
    def get_tasteScore_byname(self, name):
        reviews = self.db.child("restaurant").child(name).child("review").get()
        respondent = self.review_keyword_respondent_check(name)
        taste_count = 0
        if (respondent == 0):
            return 0
        else:
            for rev in reviews.each():
                value = rev.val()
                if (value['taste'] == 'y'):
                    taste_count += 1
            return int(taste_count/respondent*100)

    # 리뷰에 접근하여 다섯가지 키워드 별 계산하기-cost
    def get_costScore_byname(self, name):
        reviews = self.db.child("restaurant").child(name).child("review").get()
        respondent = self.review_keyword_respondent_check(name)
        cost_count = 0
        if (respondent == 0):
            return 0
        else:
            for rev in reviews.each():
                value = rev.val()
                if (value['cost'] == 'y'):
                    cost_count += 1
            return int(cost_count/respondent*100)

    # 리뷰에 접근하여 다섯가지 키워드 별 계산하기-service
    def get_serviceScore_byname(self, name):
        reviews = self.db.child("restaurant").child(name).child("review").get()
        respondent = self.review_keyword_respondent_check(name)
        service_count = 0
        if (respondent == 0):
            return 0
        else:
            for rev in reviews.each():
                value = rev.val()
                if (value['service'] == 'y'):
                    service_count += 1
            return int(service_count/respondent*100)

     # 리뷰에 접근하여 다섯가지 키워드 별 계산하기-cleanliness
    def get_cleanlinessScore_byname(self, name):
        reviews = self.db.child("restaurant").child(name).child("review").get()
        respondent = self.review_keyword_respondent_check(name)
        cleanliness_count = 0
        if (respondent == 0):
            return 0
        else:
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
        if (respondent == 0):
            return 0
        else:
            for rev in reviews.each():
                value = rev.val()
                if (value['atmosphere'] == 'y'):
                    atmosphere_count += 1
            return int(atmosphere_count/respondent*100)

    # ===== 2) 메뉴 data ======

    def insert_menu(self, name, data, img_path):
        menu_info = {
            "img_path": img_path,
            "menu_name": data['menu_name'],
            "menu_price": data['menu_price'],
            "extra_ve": data['extra_ve'],
            "extra_al": data['extra_al']
        }
        if self.menu_duplicate_check(name, data['menu_name']):
            self.db.child("restaurant").child(name).child("menu").child(data['menu_name']).set(menu_info)
            return True
        else:
            return False

    def menu_duplicate_check(self, name, menu):
        menus = self.db.child("restaurant").child(name).child("menu").get()
        if menus.each() == None:
            return True
        for res in menus.each():
            if res.key() == menu:
                return False
        return True

      # 가게 이름으로 특정 가게 메뉴 가져오기
    def get_menu_byname(self, name):
        menus = self.db.child("restaurant").child(name).child("menu").get()
        target_value = []
        for menu in menus.each():
            value = menu.val()
            target_value.append(value)
        return target_value

        # 메뉴 목록 가져오기
    def get_menus_byname(self, name):
        reviews = self.db.child("restaurant").child(
            name).child("menu").get().val()
        return reviews

    #메뉴 삭제하기 
    def remove_menu(self, name, menu):
        self.db.child("restaurant").child(name).child("menu").child(menu).remove()
        return True

    # ===== 3) 리뷰 데이터 ======
    def insert_review(self, name, data, reviewImg_path, userID):
        # 리뷰 등록 시간 DB에 저장
        now = datetime.now()
        timestamp = now.strftime('%Y.%m.%d')

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
            "reviewImg_path": reviewImg_path,
            "timestamp": timestamp,
            "userID": userID,
            "agreeUsers_num": 0
        }

        if data['nickname'] == "":
            review_info['nickname'] = "익명"
        self.db.child("restaurant").child(
            name).child("review").child(userID).set(review_info)   #userID로 리뷰 저장
        self.update_storeScore_byname(name)
        
        
     #리뷰 동의 유저 아이디 저장 
    def insert_review_agree_userId(self, name, userID, review_agree_userId):
        if self.review_agree_duplicate_check(name, userID, review_agree_userId):
            self.db.child("restaurant").child(name).child("review").child(userID).child("agree_users").push(review_agree_userId)
            #리뷰 동의한 사람 수 저장
            self.update_agreeNum_byname(name, userID)
            return True
        else:
            return False
     
    #각 리뷰에 동의한 사람 수 구하고 저장
    def update_agreeNum_byname(self, name, userID):
        agreeUsers = self.db.child("restaurant").child(name).child("review").child(userID).child("agree_users").get()
        num = []
        for agreeUserId in agreeUsers.each():
            value = agreeUserId.val()
            num.append(value)
        agreeUsers_num = len(num)
        self.db.child("restaurant").child(name).child("review").child(userID).update({"agreeUsers_num": agreeUsers_num})
        
    # 이미 동의한 리뷰인지 확인하는 함수
    def review_agree_duplicate_check(self, name, userID, review_agree_userId):
        lists = self.db.child("restaurant").child(name).child("review").child(userID).child("agree_users").get()
        if lists.each() == None:
            return True
        for res in lists.each():
            if res.val() == review_agree_userId:
                return False
        return True


    def get_review_byname(self, name):
        reviews = self.db.child("restaurant").child(name).child("review").get()
        target_value = []
        # value = reviews.val()
        # target_value.append(value)
        for rev in reviews.each():
            value = rev.val()
            target_value.append(value)
        return target_value

    # 리뷰 등록할 때마다 평점(평점, 재방문의사, 키워드5)을 업데이트
    def update_storeScore_byname(self, name):
        avgScore = self.get_avgrate_byname(name)
        tasteScore = self.get_tasteScore_byname(name)
        costScore = self.get_costScore_byname(name)
        serviceScore = self.get_serviceScore_byname(name)
        cleanlinessScore = self.get_cleanlinessScore_byname(name)
        atmosphereScore = self.get_atmosphereScore_byname(name)
        revisit = self.get_revisitrate_byname(name)
        self.db.child("restaurant").child(name).child("info").update({"store_grade": avgScore})
        self.db.child("restaurant").child(name).child("info").update({"store_taste": tasteScore})
        self.db.child("restaurant").child(name).child("info").update({"store_cost": costScore})
        self.db.child("restaurant").child(name).child("info").update({"store_service": serviceScore})
        self.db.child("restaurant").child(name).child("info").update({"store_cleanliness": cleanlinessScore})
        self.db.child("restaurant").child(name).child("info").update({"store_atmosphere": atmosphereScore})
        self.db.child("restaurant").child(name).child("info").update({"store_revisit": revisit})

    # ===== 4) 회원 data =====

    # 회원가입

    def insert_member(self, name, data, pw_hash):
        member_info = {
            "memberInfo_password": pw_hash,
            "memberInfo_name": data['memberInfo_name'],
            "memberInfo_birthDate_yy": data['memberInfo_birthDate_yy'],
            "memberInfo_birthDate_mm": data['memberInfo_birthDate_mm'],
            "memberInfo_birthDate_dd": data['memberInfo_birthDate_dd'],
            "memberInfo_gender": data['memberInfo_gender'],
            "myRestaurantList": ""
        }
        if self.id_duplicate_check(name):
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

    # 로그인
    def find_user(self, id_, pw_):
        users = self.db.child("member").get()
        target_value = []
        for res in users.each():
            value = res.val()

            if res.key() == id_ and value['memberInfo_password'] == pw_:
                return True

        return False

    # ===== 5) 내가 찜한 맛집 data =====
    def check_mylist_is_empty(self, userId):
        myrestaurants = self.db.child("member").child(userId).child("myRestaurantList").get()
        if myrestaurants.each() == None:
            return True
        else:
            return False
    
    # DB 마이리스트 읽어오기
    def get_mylist(self, userId):
        myrestaurants = self.db.child("member").child(userId).child("myRestaurantList").get()
        target_value = []
        for res in myrestaurants.each():
            value = res.val()
            target_value.append(self.get_restaurant_byname(value))
        new_dict = {}
        for k, v in enumerate(target_value):
            new_dict[k] = v
        return new_dict

    # 찜하기 버튼으로 마이리스트에 추가하기
    def insert_mylist(self, name, userId):
        if self.mylist_duplicate_check(name, userId):
            self.db.child("member").child(userId).child("myRestaurantList").push(name)
            return True
        else:
            return False
        
    # 찜하기 버튼으로 마이리스트에 삭제하기
    def delete_mylist(self, name, userId):
        lists = self.db.child("member").child(userId).child("myRestaurantList").get()
        for res in lists.each():
            if res.val() == name:
                key=res.key()
                self.db.child("member").child(userId).child("myRestaurantList").child(key).remove()
                break
        return True

    # 이미 찜리스트에 있는 가게인지 확인하는 함수
    def mylist_duplicate_check(self, name, userId):
        lists = self.db.child("member").child(userId).child("myRestaurantList").get()
        if lists.each() == None:
            return True
        for res in lists.each():
            if res.val() == name:
                return False
        return True
    
        
    #내찜맛 리스트에 해당 가게 이름이 있는지 확인하는 함수
    def res_in_myRestaurantlist_check(self, name, userId):
       myrestaurants = self.db.child("member").child(userId).child("myRestaurantList").get()
       if myrestaurants.each() == None:
           return 0
       for res in myrestaurants.each():
           if res.val()==name:
               return 1
       return 0

        
