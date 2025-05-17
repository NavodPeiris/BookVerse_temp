const prod = false
const ingress_ip = "localhost" // this is localhost as we run k8s locally

const auth_link = prod ? `http://${ingress_ip}/auth`: "http://localhost:8001/auth"
const book_catalog_link = prod ? `http://${ingress_ip}/book-catalog`: "http://localhost:8002/book-catalog"
const book_pub_buy_link = prod ? `http://${ingress_ip}/book-pub-buy`: "http://localhost:8003/book-pub-buy"
const book_review_recommend_link = prod ? `http://${ingress_ip}/book-review-recommend`: "http://localhost:8004/book-review-recommend"
const minio_link = "http://localhost:9000"

export {
    auth_link,
    book_catalog_link,
    book_pub_buy_link,
    book_review_recommend_link,
    minio_link
}