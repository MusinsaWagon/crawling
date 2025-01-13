import requests

def get_review_summary(catalog_product_id, limit_count=5, order="BEST_SCORE_DESC"):

    # catalog_product_id (str): 상품 ID
    # limit_count (int): 가져올 리뷰 제한 수 (기본값: 5)
    # order (str): 리뷰 정렬 기준 (기본값: "BEST_SCORE_DESC")

    url = "https://api.zigzag.kr/api/2/graphql/GetPdpIntegratedData"

    # 요청 헤더
    headers = {
        "Content-Type": "application/json",
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # 요청 페이로드
    payload = {
        "operationName": "GetPdpIntegratedData",
        "variables": {
            "catalog_product_id": catalog_product_id,
            "limit_count": limit_count,
            "order": order
        },
        "query": """
        query GetPdpIntegratedData(
            $catalog_product_id: ID!, 
            $limit_count: Int, 
            $order: ProductReviewListOrderType
        ) {
            related_product_review_summary(product_id: $catalog_product_id) {
                all_count
                ratings_average
            }
            product_review_list(
                product_id: $catalog_product_id, 
                limit_count: $limit_count, 
                order: $order
            ) {
                item_list {
                    id
                    contents
                    rating
                    reviewer {
                        profile {
                            masked_email
                        }
                    }
                }
            }
        }
        """
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status() 

        data = response.json()
        
        review_summary = data.get("data", {}).get("related_product_review_summary", {})
        total_reviews = review_summary.get("all_count", 0)
        average_rating = review_summary.get("ratings_average", 0.0)

        return {
            "total_reviews": total_reviews,
            "average_rating": average_rating
        }
    except requests.exceptions.RequestException as e:
        print(f"HTTP 평점 요청 에러: {e}")
    except Exception as e:
        print(f"평점 요청 오류 발생: {e}")
        return None


# 사용 예제
if __name__ == "__main__":
    catalog_product_id = "116803378"
    review_summary = get_review_summary(catalog_product_id)

    if review_summary:
        print(f"총 리뷰 수: {review_summary['total_reviews']}")
        print(f"평균 평점: {review_summary['average_rating']}")
    else:
        print("리뷰 정보를 가져오지 못했습니다.")