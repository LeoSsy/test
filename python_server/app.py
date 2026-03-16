from flask import Flask, request, jsonify
import requests
import os
import time
import hmac
import hashlib
from dotenv import load_dotenv
from volcenginesdkarkruntime import Ark

# 加载环境变量
load_dotenv()

app = Flask(__name__)

api_key = os.getenv("ARK_API_KEY")
base_api_url = os.getenv("ARK_BASE_URL")

# 文生图 图生图模型
image_model_name ="doubao-seedream-4-5-251128"

client = Ark(base_url=base_api_url, api_key=api_key)


# 豆包seed
def ark_text_2_image(prompt):
    image_res = client.images.generate(
        model=image_model_name,
        prompt=prompt,
        size="2k",
        # output_format="png",
        response_format="url",
        watermark=False,
    )
    return image_res.to_json()


def ark_textImage_2_image(prompt, image_url):
    res = client.images.generate(
        model=image_model_name,
        prompt=prompt,
        image=image_url,
        size="2k",
        output_format="png",
        response_format="url",
        watermark=False,
    )
    return res.to_json()


def arc_multi_image_2_image(prompt, image_urls):
    res = client.images.generate(
        model=image_model_name,
        prompt=prompt,
        image=image_urls,
        size="2k",
        sequential_image_generation="disabled",
        output_format="png",
        response_format="url",
        watermark=False,
    )
    return res.to_json()


def arc_video_create(prompt, images):
    content = [
        {"type": "text", "text": prompt},
    ]
    for url in images:
         content.append({
            "type" : "image_url",
            "image_url" : {
                "url" : url
            },
            "role" : "reference_image"
        })
    print(f"arc_video_create:content----->{content}")
    res = client.content_generation.tasks.create(
        model="doubao-seedance-1-0-lite-i2v-250428",
        content=content,
        resolution="720p",
        ratio="16:9",
        duration=5,
        watermark=False,
    )
    print(f"arc_video_create:res----->{res}")
    return res.to_json()

def arc_video_status(video_task_id):
    res = client.content_generation.tasks.get(
        task_id=video_task_id
    )
    return res.to_json()

def ark_images_2_images(prompt,images):
    res = client.images.generate(
        model=image_model_name,
        prompt=prompt,
        image=images,
        size="2K",
        sequential_image_generation="disabled",
        output_format="png",
        response_format="url",
        watermark=False
    )
    print(f"ark_images_2_images---: {res}")
    return res.to_json()

# 生成签名
def generate_signature(method, path, timestamp, body):
    content = f"{method}\n{path}\n{timestamp}\n{body}"
    signature = hmac.new(
        VOLCENGINE_SECRET_KEY.encode("utf-8"), content.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return signature


# 通用API调用函数
def call_volcengine_api(endpoint, data):
    method = "POST"
    path = endpoint
    timestamp = str(int(time.time()))
    body = str(data)

    signature = generate_signature(method, path, timestamp, body)

    headers = {
        "Content-Type": "application/json",
        "X-Timestamp": timestamp,
        "X-Access-Key": VOLCENGINE_ACCESS_KEY,
        "X-Signature": signature,
    }

    response = requests.post(f"{VOLCENGINE_API_URL}{path}", headers=headers, json=data)
    return response.json()


# 对话脚本生成API
def generate_dialogue_script(prompt):
    data = {
        "model": "ep-20240316164822-d58k5",  # 替换为实际的模型ID
        "input": prompt,
        "parameters": {"max_new_tokens": 1000, "temperature": 0.7},
    }
    return call_volcengine_api("/chat/completions", data)


# 文生图API
def text_to_image(prompt):
    data = {
        "model": "ep-20240316164822-d58k5",  # 替换为实际的文生图模型ID
        "input": prompt,
        "parameters": {"size": "1024x1024", "n": 1},
    }
    return call_volcengine_api("/images/generations", data)


# 图生视频API
def image_to_video(image_url):
    data = {
        "model": "ep-20240316164822-d58k5",  # 替换为实际的图生视频模型ID
        "input": {"image_url": image_url},
        "parameters": {"duration": 10, "resolution": "1080p"},
    }
    return call_volcengine_api("/videos/generations", data)


@app.route("/v1/images/generations", methods=["POST"])
def text2image():
    try:
        data = request.get_json()
        prompt = data.get("prompt")
        if not prompt:
            return jsonify({"error": "Missing prompt parameter"}), 400
        result = ark_text_2_image(prompt)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/v1/images2images", methods=["POST"])
def images2images():
    try:
        data = request.get_json()
        prompt = data.get("prompt")
        images = data.get("images")
        print(f"prompt---{prompt}--images---{images}")
        if not prompt:
            return jsonify({"error": "Missing prompt parameter"}), 400
        result = ark_images_2_images(prompt,images)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/image2video", methods=["POST"])
def image2video():
    try:
        data = request.get_json()
        image_url = data.get("image_url")
        if not image_url:
            return jsonify({"error": "Missing image_url parameter"}), 400
        result = image_to_video(image_url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/v1/videoStatus/<int:task_id>", methods=["GET"])
def videoStatus(task_id):
    try:
        if not task_id:
            return jsonify({"error": "Missing video_task_id parameter"}), 400
        result = arc_video_status(task_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/v1/image2video", methods=["POST"])
def image2videos():
    try:
        data = request.get_json()
        prompt = data.get("prompt")
        images = data.get("images")
        if not images:
            return jsonify({"error": "缺少参考图参数 images"}), 400
        result = arc_video_create(prompt=prompt,images=images)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
