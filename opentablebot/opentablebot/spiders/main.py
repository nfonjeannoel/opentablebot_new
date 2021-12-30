import json

import requests


def get_api_images(rid):
    url = "https://www.opentable.ca/dapi/fe/gql"
    payload = json.dumps({
        "operationName": "PhotoGallery",
        "variables": {
            "restaurantId": int(rid),
            "pageSize": 100,
            "pageNumber": 1,
            "instagramOptOut": True,
            "foodSpottingOptOut": False,
            "includeProfile": True,
            "includeGooglePhotos": True
        },
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "7b9116479d88bd3012ef99131ea33a438e0bb5c07fccd7861acc412070d117a3"
            }
        }
    })
    headers = {
        'x-csrf-token': 'c672c21e-9e34-4ecf-a892-0d173a44cc49',
        'content-type': 'application/json',
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    response = json.loads(response.text)
    image_json = {}
    cat_list = response['data']['restaurant']['photos']['gallery']['categories']
    for cat in cat_list:
        image_json[cat['name']] = []
    image_list = response['data']['restaurant']['photos']['gallery']['photos']  # list of phots
    for image in image_list:
        images = []
        for image_size in image['thumbnails']:
            images.append({
                "img_url": image_size.get('url'),
                "dimension": f"{image_size.get('width')} x {image_size.get('height')} ({image_size.get('label')})"
            })

        image_json[image['category']].append(images)

    return image_json


def getJson(expr):
    expr = expr.split('"menus":')
    if len(expr) < 2:
        print("less than 2")
        return
    expr = expr[1]
    # print(expr)
    stack = []
    for ind, char in enumerate(expr):
        if char in ["(", "{", "["]:
            stack.append(char)
        elif char not in [")", "}", "]"]:
            pass
        else:
            if not stack:
                # print("stack is empty")
                return False
            # print(f" stack is {stack}")
            current_char = stack.pop()
            # print(f" we poped {current_char} from stack")
            if current_char == '(':
                if char != ")":
                    return False
            if current_char == '{':
                if char != "}":
                    return False
            if current_char == '[':
                if char != "]":
                    return False
            if not stack:
                # for i in range(10):
                #     print("*"*20)
                #     print()
                # print(f"end index {ind}")
                return json.loads(expr[0:ind + 1])


def get_ird(param):
    rid = 0
    for c in param.split():
        if "rid" in c:
            for i in c.split(","):
                if "rid" in i:
                    try:
                        rid = int(i[6:])
                    except:
                        continue
    return rid


def get_menu(raw_lst):
    menus_list = []
    for section in raw_lst:
        data = {"title": section.get("title", "NA"), "currency": section.get("currency", "NA"),
                "description": section.get("description", "NA"), "sections": section.get("sections", "NA")}

        menus_list.append(data)
    return menus_list


# def get_image_list(myresult):
#     img_list = []
#     for test in myresult:
#         build = False
#         res = ""
#         for char in test:
#             if char == ")":
#                 img_list.append(res)
#                 break
#             if build:
#                 res += char
#             if char == "(":
#                 build = True
#     return img_list
