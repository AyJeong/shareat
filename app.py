from flask import Flask, render_template, request, flash, redirect, url_for, session
from database import DBhandler
import math
import hashlib
import sys
from urllib import parse

app = Flask(__name__)

DB = DBhandler()


# ===== [페이지 경로 설정] =====


@app.route("/")
def goTo_mainHome():
    return redirect(url_for("list_restaurants"))

# 메인홈(맛집 리스트)
@app.route("/shareat")
def list_restaurants():
    page = request.args.get("page", 0, type=int)
    category = request.args.get("category", "all")  # 선택한 맛집 카테고리 값
    sort = request.args.get("sort", "grade")   # 선택한 목록 정렬 순서 기준

    category = request.args.get("category", "all")  # 선택한 맛집 카테고리 값
    sort = request.args.get("sort", "grade")   # 선택한 목록 정렬 순서 기준

    limit = 9
    start_idx = limit*page
    end_idx = limit*(page+1)

    # 선택한 카테고리 맛집 목록 추출
    if category == "all":
        data = DB.get_restaurants()
    else:
        data = DB.get_restaurants_bycategory(category)

    # 맛집 목록 순서 정렬 (평점순/최신순)
    if sort == "grade":
        data = dict(
            sorted(data.items(), key=lambda x: x[1]['info']['store_grade'], reverse=True))
    else:
        data = dict(
            sorted(data.items(), key=lambda x: x[1]['time']['timestamp'], reverse=True))

    if data == None:
        count = 0    # 등록된 맛집 개수
        return render_template("index.html", total=count, page=page)
    else:
        count = len(data)
        data = dict(list(data.items())[start_idx: end_idx])
        page_count = len(data)

        return render_template("index.html", datas=data.items(), total=count, limit=limit, page=page, page_count=math.ceil(count/9), category=category, sort=sort)

# 내찜맛 화면 출력
@app.route("/myRestaurantList")
def goTo_myRestaurantList():
    userId = session['id']
    page = request.args.get("page", 0, type=int)
    limit = 9

    start_idx = limit*page
    end_idx = limit*(page+1)
    data = []

    if DB.check_mylist_is_empty(userId):
        count = 0
        return render_template("myRestaurantList.html", datas=data, total=count, limit=limit, page=page, page_count=int((count/9)+1))
    else:
        data = DB.get_mylist(userId)  # 찜한 맛집 리스트 데이터
        count = len(data)
        list_data = dict(list(data.items())[start_idx:end_idx])
        return render_template("myRestaurantList.html", datas=list_data.items(), total=count, limit=limit, page=page, page_count=int((count/9)+1))

# 맛집 상세정보 페이지
@app.route("/detail-info/<name>")
def goTo_detailInfo(name):
    data = DB.get_restaurant_byname(str(name))
    img_paths=DB.get_restaurant_imgs_byname(str(name))
    if session:
        likechecked = DB.res_in_myRestaurantlist_check(name=name, userId=session['id'])
        return render_template("detailInfo_restaurantInfo.html", data=data, name=name, likechecked=likechecked, img_paths=img_paths)
    else:
        return render_template("detailInfo_restaurantInfo.html", data=data, name=name, img_paths=img_paths)


# 찜하기 버튼누르면 데베에 추가하고 다시 맛집 상세정보 페이지로 이동
@app.route("/submit_like_post", methods=['POST'])
def submit_like_post():
    data = request.form
    name = data["store_name"]
    userId = data["userId"]
    if DB.insert_mylist(name, userId):
        #flash("내가 찜한 맛집 리스트에 추가 되었습니다.")
        return redirect(url_for("goTo_detailInfo", name=name))
    elif DB.delete_mylist(name, userId):
        #flash("내가 찜한 맛집 리스트에서 삭제 되었습니다.")
        return redirect(url_for("goTo_detailInfo", name=name))

# 메뉴 상세 정보 페이지
@app.route("/detail-menu/<name>")
def goTo_detailMenu(name):
    data = DB.get_restaurant_byname(str(name))
    menu = DB.get_menus_byname(str(name))

    if menu == None:
        count = 0    # 등록된 메뉴 개수
        # total=count
        return render_template("detailInfo_menu.html", data=data, name=name, total=count)

    else:
        menu_data = DB.get_menu_byname(str(name))
        count = len(menu)
        # total=count
        return render_template("detailInfo_menu.html", menu_data=menu_data, data=data, name=name, total=count)

# 대표메뉴 삭제 버튼 누르면 데베에서 삭제하고 다시 대표메뉴 페이지로 이동
@app.route("/submit_remove_post", methods=['POST'])
def submit_remove_post():
    data = request.form
    name = data["store_name"]
    menu = data["menu_name"]
    print(name)
    print(menu)
    if DB.remove_menu(name, menu):
        flash("대표 메뉴가 삭제되었습니다.")
        return redirect(url_for("goTo_detailMenu", name=name, menu=menu))

# 리뷰 상세 정보 페이지
@app.route("/detail-review/<name>")
def goTo_detailReiview(name):
    data = DB.get_restaurant_byname(str(name))
    rev = DB.get_reviews_byname(str(name))
    print(rev)

    if rev == None:
        count = 0    # 등록된 리뷰 개수
        # total=count
        return render_template("detailInfo_review.html", data=data, name=name, total=count)

    else:
        review_data = DB.get_review_byname(str(name))
        count = len(rev)
        return render_template("detailInfo_review.html", review_data=review_data, data=data, name=name, total=count)


# 맛집 등록 페이지
@app.route("/registration-restaurant")
def goTo_registerRestaurant():
    return render_template("registerRestaurantInfo.html")


# 메뉴 등록 페이지
@app.route("/registration-menu")
def goTo_registerMenu():
    return render_template("registerMenu.html")


# 맛집 수정 페이지
@app.route("/modify-info/<name>")
def goTo_modifyInfo(name):
    data = DB.get_restaurant_byname(str(name))
    return render_template("modifyRestaurantInfo.html", data=data, name=name)

# 메뉴 추가 페이지
@app.route("/add-menu/<name>")
def goTO_addMenu(name):
    return render_template("registerMenu.html", name=name)


# 리뷰 등록 페이지
@app.route("/review")
def goTo_writeReview():
    return render_template("writeReview.html")


# 리뷰 등록 - 가게 이름 받아오기
@app.route("/review_storeName_post", methods=['POST'])
def reg_storeName_review_post():
    data = request.form['store_name']
    return render_template("writeReview.html", name=data)


# 로그인 페이지
@app.route("/login")
def goTo_login():
    return render_template("login.html")


# 회원가입 페이지
@app.route("/signup")
def goTo_signup():
    return render_template("signup.html")


# ===== [사용자 입력 데이터 받아오기] =====

# 가게정보 등록
@app.route("/submit_restaurantData_post", methods=['POST'])
def reg_restaurantData_submit_post():
    global idx
    files = request.files.getlist("file[]")
    data = request.form
    img_paths=[]
    for fil in files:
        if fil.filename == '':
            image_path = "../static/image_slides/default_image.png"
            img_paths.append(image_path)
            break
        else:
            fil.save("./static/image/{}".format(fil.filename))
            image_path = "../static/image/{}".format(fil.filename)
            img_paths.append(image_path)
        
    if DB.insert_restaurant(data['store_name'], data, img_paths):
        return redirect(url_for("list_restaurants"))
    else:
        flash ("이미 존재하는 가게입니다")
        return redirect(url_for("list_restaurants"))

# 가게정보 수정

@app.route("/modify_restaurantData_post", methods=['POST'])
def mod_restaurantData_submit_post():
    global idx
    files = request.files.getlist("file[]")
    data = request.form
    name = data["store_name"]
    img_paths=[]
    for fil in files:
        if fil.filename == '':
            image_path = "./static/image_slides/default_image.png"
            img_paths.append(image_path)
            break
        else:
            fil.save("./static/image/{}".format(fil.filename))
            image_path = "../static/image/{}".format(fil.filename)
            img_paths.append(image_path)
            
    if DB.modify_restaurant(data['store_name'], data, img_paths):
        return redirect(url_for("goTo_detailInfo", name=name))
    else:
        flash("가게 이름을 변경 할 수 없습니다 !")
        return render_template("modifyRestaurantInfo.html")


@app.route("/submit_storeName_post", methods=['POST'])  # 가게 이름
def reg_storeName_submit_post():
    data = request.form['store_name']
    print(data)
    return render_template("registerMenu.html", name=data)


# 데이터베이스에 회원정보 넣기
@app.route("/submit_signupData_post", methods=['POST'])
def reg_signupData_submit_post():
    data = request.form
    pw = request.form['memberInfo_password']
    rePw = request.form['memberInfo_rePassword']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    rePw_hash = hashlib.sha256(rePw.encode('utf-8')).hexdigest()

    if pw_hash == rePw_hash:
        if DB.insert_member(name=data['memberInfo_id'], data=data, pw_hash=pw_hash):
            return render_template("login.html")
        else:
            flash("이미 가입된 아이디이거나 비밀번호가 일치하지 않습니다.")
            return render_template("signup.html")
    else:
        flash("비밀번호 재확인이 비밀번호와 일치하지 않습니다.")
        return render_template("signup.html")


@ app.route("/submit_loginData_post", methods=['POST'])
def reg_loginData_submit_post():
    id_ = request.form['input_id']
    pw = request.form['input_password']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

    if DB.find_user(id_, pw_hash):
        session['id'] = id_
        return redirect(url_for("list_restaurants"))
    else:
        flash("Wrong ID or PW!")
        return render_template("login.html")


# 로그아웃
@app.route("/logout")
def logout_user():
    session.clear()
    return redirect(url_for("list_restaurants"))


# [사용자 입력 데이터 받아오기] - 메뉴
@ app.route("/submit_menuData_post", methods=['POST'])
def reg_menuData_submit_post():
    global idx
    data = request.form
    image_file = request.files["file"]
    name = data['store_name']
    if image_file.filename != '':
        image_file.save("./static/image/"+image_file.filename)
        img_path = "../static/image/"+image_file.filename
    else:
        img_path = "../static/image/grey.png"
        
    if DB.insert_menu(name, data, img_path):
        flash("대표 메뉴가 등록이 완료되었습니다")
        return redirect(url_for("goTo_detailMenu", name=name))
    else:
        flash("해당 메뉴가 이미 있습니다")
        return redirect(url_for("goTo_detailMenu", name=name))


# [사용자 입력 데이터 받아오기] - 리뷰
@app.route("/submit_reviewData_post", methods=['POST'])
def reg_reviewData_submit_post():
    global idx
    image_file = request.files["picture"]
    if image_file.filename != '':
        image_file.save("./static/image/"+image_file.filename)
        reviewImg_path = "../static/image/"+image_file.filename
    else:
        reviewImg_path = "../static/image/grey.png"

    data = request.form
    name = data['store_name']
    userID = data['userID']

    DB.insert_review(name, data, reviewImg_path, userID)

    return redirect(url_for("goTo_detailReiview", name=name))


@app.route("/submit_review_agree_userId", methods=['POST'])
def submit_review_agree_userId():
    data = request.form
    name = data['store_name']
    userID = data['userID']
    review_agree_userId = data['review_agree_userId']
    DB.insert_review_agree_userId(name, userID, review_agree_userId)

    return redirect(url_for("goTo_detailReiview", name=name))


@app.route("/submit_review_userID", methods=['POST'])
def submit_review_userID():
    data = request.form
    name = data['store_name']
    userID = data['userID']
    return redirect(url_for("goTo_detailReiview", name=name))


app.secret_key = 'super secret key'

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    app.config['SESSION_TYPE'] = 'filesystem'
