import streamlit as st
import requests
import json
import re
import time

# ===== CẤU HÌNH GIAO DIỆN =====
st.set_page_config(page_title="Shopee Advanced Tool", layout="wide")
st.title("Chuyển Đổi Link Shopee ")

# ===== HÀM XỬ LÝ COOKIE THÔNG MINH =====
def process_cookie_input(raw_input):
    """
    Hàm này tự động phát hiện xem đầu vào là JSON hay chuỗi thường
    và convert về dạng chuẩn: key=value; key2=value2
    """
    if not raw_input:
        return ""
        
    try:
        # 1. Thử parse xem có phải là JSON không
        cookie_data = json.loads(raw_input)
        
        # Trường hợp 1: JSON dạng object có chứa key "cookies" (như mẫu bạn gửi)
        if isinstance(cookie_data, dict) and "cookies" in cookie_data:
            cookies_list = cookie_data["cookies"]
        # Trường hợp 2: JSON là một list ngay từ đầu
        elif isinstance(cookie_data, list):
            cookies_list = cookie_data
        else:
            # JSON hợp lệ nhưng không đúng cấu trúc mong muốn -> coi như chuỗi thường hoặc lỗi
            return raw_input

        # Convert list object thành chuỗi key=value;
        formatted_cookies = []
        for c in cookies_list:
            # Lấy name và value, bỏ qua nếu thiếu
            if "name" in c and "value" in c:
                formatted_cookies.append(f"{c['name']}={c['value']}")
        
        return "; ".join(formatted_cookies)

    except json.JSONDecodeError:
        # 2. Nếu lỗi JSON -> Đây là chuỗi cookie thô (key=value;...)
        # Trả về nguyên bản
        return raw_input

# ===== LOAD VÀ XỬ LÝ COOKIE =====
try:
    raw_cookie_secret = st.secrets["SPC_F=yXx3sQweqMibX0VWnstyqSwKDzpFT1Fs; REC_T_ID=bdb90805-2310-11f0-8d09-b6e08496fef4; SPC_CLIENTID=eVh4M3NRd2VxTWlifgxhsltxaspioibi; _hjSessionUser_868286=eyJpZCI6IjY1N2QzYjQ3LWM3MjItNTAyOS04MjZiLWVhOTRhYmY4NmMyYSIsImNyZWF0ZWQiOjE3NDU3MjE1MjY0MzQsImV4aXN0aW5nIjp0cnVlfQ==; _QPWSDCXHZQA=a3bddc90-ba62-4dec-c965-a3b409c6bd92; REC7iLP4Q=4c963780-d3f5-46d4-8e70-39ff4556ece2; _fbp=fb.1.1754207522929.891955255371700356; _ga_FV78QC1144=GS2.1.s1759491737$o2$g0$t1759491739$j58$l0$h0; _ga_QLZF8ZGF0S=GS2.1.s1761396864$o68$g1$t1761396904$j20$l0$h0; _gcl_au=1.1.1205492329.1761998368; language=vi; SPC_U=-; SPC_T_ID=/fud3vQDyDl9/ItLg+kvrVJeuYOyDFMjaH4QLvdkTw8962Z1lVK01J8s58eldkhOt9AghrUIQRKaX+Y9eMpLfBx1zB4ZyqrYKO1woPHGgD1pCBLiB039C5eFYTydbkUH2eEhJ4BP27p11geLO6nRE47DBL6/XJQlW4MLlmjAw9Q=; SPC_T_IV=WXR5TEF3aGdBemFqQXlKQw==; SPC_R_T_ID=/fud3vQDyDl9/ItLg+kvrVJeuYOyDFMjaH4QLvdkTw8962Z1lVK01J8s58eldkhOt9AghrUIQRKaX+Y9eMpLfBx1zB4ZyqrYKO1woPHGgD1pCBLiB039C5eFYTydbkUH2eEhJ4BP27p11geLO6nRE47DBL6/XJQlW4MLlmjAw9Q=; SPC_R_T_IV=WXR5TEF3aGdBemFqQXlKQw==; SPC_ST=.T0lNMTk0TXIyYURQanBpMaWtJ70ekPAjii0uaoF1VRIUajuqztTVOaGXGGBivDl4VO/iZ9EJPUH2fKfVJyTHsFLOgpYKKGiTE2Rajz+e5O1uCOOvvXGyEJsR7x0s085MVFyf8SzIfMGJVy0rfINEdIJVovv8e9EGrdQXDfsQNUOVuvs5gz8mg1HfhHeHxp7T1Qy/nxqKfY4ATYv6YQQKmxjfuw3Ws8Zd7GWgHRzJhnAbkI5Gl5PpAHEPM0NnypsbSqI8vnewen1SeyGXJqKi3A==; SPC_EC=.cDFGZ0tuV1poZTF3dzhKczVQkPslboLZBYm9PgfzR+4anpH2FKkL1a5AvFuKC6p0oeHxKcOj+O4djv04qCDFay/Do+9i7pC/+xhfVYORldfbxCY3wOPOs1FnB2FWNqeJA+E/dmCO4NQuu+q5VGOR90yCnT/UeffJx/N22EGcgtuvpi5mwU77ty+11wqONS7+v8QxuRj3xe/0pKQlPHrWK9gkPRBlZGMb2C+2ZYjbUsKXvyeORv4xLYjNEC9kFnrJft6BW26MJkQHGJOFOD1n4A==; language=vi; _sapid=d79a6104a6036c6cc2bc4d37c7714ca5f2af2013511554634ce11d9f; _gid=GA1.2.150986598.1769690557; link_social_media_1529987610=1; shopee_webUnique_ccd=Dwl9ahJDMrBca2EaRLfObg%3D%3D%7CimDzMR5MA2AEArCgTsEtOrljRCIE4u3zbw1lcdxoWif4ooy2n%2BIphQSGHefMV0OdVy0ND6Bx0l2isA%3D%3D%7CkM49PQ7rqyzpYinT%7C08%7C3; ds=69d27ca5f91466ef9a07cd957c07a54e; _ga=GA1.2.989314910.1745721526; _ga_4GPP1ZXG63=GS2.1.s1769743280$o166$g1$t1769743347$j60$l0$h1750047784; _dc_gtm_UA-61914164-6=1"]
    # Gọi hàm xử lý để convert JSON sang chuỗi chuẩn (nếu cần)
    cookie_str = process_cookie_input(raw_cookie_secret)
except Exception:
    st.error("Chưa cấu hình 'SHOPEE_COOKIE' trong Secrets!")
    st.stop()

# Kiểm tra nhanh xem cookie có hợp lệ không
if not cookie_str or "=" not in cookie_str:
    st.warning("Cảnh báo: Format Cookie có vẻ không đúng. Hãy kiểm tra lại Secrets.")

# ===== KHU VỰC CẤU HÌNH SUB_ID (DÙNG CHUNG) =====
with st.expander("Cấu hình SubID (Tùy chọn)", expanded=False):
    cols = st.columns(5)
    sub_ids = {}
    for i, col in enumerate(cols):
        val = col.text_input(f"SubID {i+1}", key=f"sub_{i+1}")
        if val.strip():
            sub_ids[f"subId{i+1}"] = val.strip()

# ===== HÀM GỌI API (XỬ LÝ CHUNK 50 LINK) =====
def call_shopee_api(links_batch, sub_ids_dict):
    """
    Hàm này nhận vào list tối đa 50 links và trả về danh sách kết quả tương ứng.
    """
    URL = "https://affiliate.shopee.vn/api/v3/gql?q=batchCustomLink"
    
    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br", 
        "accept-language": "vi,en-US;q=0.9,en;q=0.8,fr-FR;q=0.7,fr;q=0.6",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "cookie": cookie_str, # Đã được xử lý chuẩn format
        "origin": "https://shopee.vn",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://shopee.vn/",
        "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    }

    # Xây dựng linkParams
    link_params = []
    for link in links_batch:
        item = {"originalLink": link}
        if sub_ids_dict:
            item["advancedLinkParams"] = sub_ids_dict
        link_params.append(item)

    payload = {
        "operationName": "batchGetCustomLink",
        "query": """
        query batchGetCustomLink($linkParams: [CustomLinkParam!], $sourceCaller: SourceCaller) {
          batchCustomLink(linkParams: $linkParams, sourceCaller: $sourceCaller) {
            shortLink
            longLink
            failCode
          }
        }
        """,
        "variables": {
            "linkParams": link_params,
            "sourceCaller": "CUSTOM_LINK_CALLER"
        }
    }

    try:
        resp = requests.post(URL, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('data', {}).get('batchCustomLink', [])
        else:
            # Silent fail hoặc log nhẹ
            return []
    except Exception as e:
        return []

# ===== GIAO DIỆN TABS =====
tab1, tab2 = st.tabs(["📋 Chuyển đổi danh sách Link", "📝 Chuyển đổi bài viết (Content)"])

# ================= TAB 1: DANH SÁCH LINK =================
with tab1:
    st.write("Nhập danh sách link Shopee (mỗi link 1 dòng):")
    raw_input = st.text_area("Input Links", height=200, placeholder="https://shopee.vn/sp1...\nhttps://shopee.vn/sp2...")
    
    if st.button("🚀 Chuyển Đổi Link", key="btn_tab1"):
        if not raw_input.strip():
            st.warning("Vui lòng nhập link!")
        else:
            input_links = [line.strip() for line in raw_input.split('\n') if line.strip()]
            total_links = len(input_links)
            st.info(f"Đã tìm thấy {total_links} links. Đang xử lý...")

            final_short_links = []
            
            # Chia nhỏ thành từng chunk 50 link
            batch_size = 50
            progress_bar = st.progress(0)
            
            for i in range(0, total_links, batch_size):
                chunk = input_links[i : i + batch_size]
                results = call_shopee_api(chunk, sub_ids)
                
                if results:
                    for res in results:
                        if res.get('shortLink'):
                            final_short_links.append(res['shortLink'])
                        else:
                            final_short_links.append(f"ERROR_FAIL_CODE_{res.get('failCode')}")
                else:
                    final_short_links.extend(["API_ERROR"] * len(chunk))
                
                progress_bar.progress(min((i + batch_size) / total_links, 1.0))
                time.sleep(0.1)

            st.success("Hoàn tất! Bấm vào nút Copy ở góc phải bên dưới 👇")
            result_text = "\n".join(final_short_links)
            
            # --- Thay đổi: Dùng st.code để có nút copy ---
            st.code(result_text, language="text")

# ================= TAB 2: CHUYỂN ĐỔI CONTENT =================
with tab2:
    st.write("Dán toàn bộ bài viết quảng cáo vào đây. Tool sẽ tự tìm link `s.shopee.vn` và thay thế bằng link Affiliate của bạn.")
    content_input = st.text_area("Input Content", height=200, placeholder="Siêu sale tại https://s.shopee.vn/xyz ...")

    if st.button("🔄 Chuyển Đổi Link", key="btn_tab2"):
        if not content_input.strip():
            st.warning("Vui lòng nhập nội dung!")
        else:
            # Regex bắt link https://s.shopee.vn/xxxxx
            found_links = re.findall(r'(https?://s\.shopee\.vn/[a-zA-Z0-9]+)', content_input)
            unique_links = list(set(found_links))
            
            if not unique_links:
                st.warning("Không tìm thấy link s.shopee.vn nào trong bài viết!")
            else:
                st.info(f"Tìm thấy {len(unique_links)} link rút gọn. Đang xử lý...")
                
                link_mapping = {}
                batch_size = 50
                
                for i in range(0, len(unique_links), batch_size):
                    chunk = unique_links[i : i + batch_size]
                    results = call_shopee_api(chunk, sub_ids)
                    
                    if results and len(results) == len(chunk):
                        for original, res in zip(chunk, results):
                            if res.get('shortLink'):
                                link_mapping[original] = res['shortLink']
                    
                final_content = content_input
                count_success = 0
                for old_link, new_link in link_mapping.items():
                    if new_link:
                        final_content = final_content.replace(old_link, new_link)
                        count_success += 1
                
                st.success(f"Đã thay thế thành công {count_success}/{len(unique_links)} link! Bấm vào nút Copy ở góc phải bên dưới 👇")
                
                # --- Thay đổi: Dùng st.code để có nút copy ---
                st.code(final_content, language="markdown")




