from locust import HttpUser, task, between
from random import choice


class HouseTestUser(HttpUser):
    host = "http://192.168.0.103:8000"
    wait_time = between(1, 5)

    @task(1)
    def get_house_list(self):
        self.client.get("/houses/")

    # @task(2)
    # def get_house_detail(self):
    #     house_id = choice([13, 14, 15, 16, 45])
    #     self.client.get(f"/houses/{house_id}/")
    #
    # @task(1)
    # def get_filtered_house_list(self):
    #     self.client.get("/houses/filter/")
    #
    # @task(1)
    # def get_purchase_house_list(self):
    #     self.client.get("/houses/purchase/")
    #
    # @task(1)
    # def get_purchase_house_detail(self):
    #     house_id = choice([1, 12, 13, 15])
    #     self.client.get(f"/houses/purchase/{house_id}/")
    #
    # @task(1)
    # def get_filter_options(self):
    #     self.client.get("/filter-options/")
    #
    # @task(1)
    # def get_filter_option_detail(self):
    #     filter_id = choice([1, 2, 3])
    #     self.client.get(f"/filter-options/{filter_id}/")
    #
    # @task(1)
    # def get_category_list(self):
    #     self.client.get("/category/")

    # @task(1)
    # def get_category_detail(self):
    #     category_slug = choice(["karkasnye-doma", "doma-iz-ocilindrovannogo-brevna", "doma-iz-kleenogo-brusa"])
    #     self.client.get(f"/categories/{category_slug}/")
    #
    # @task(1)
    # def get_finishing_options(self):
    #     self.client.get("/finishing-options/")
    #
    # @task(1)
    # def get_document_list(self):
    #     self.client.get("/houses-document/")
    #
    # @task(1)
    # def get_review_list(self):
    #     self.client.get("/reviews/")
    #
    # @task(1)
    # def get_order_list(self):
    #     self.client.get("/orders/")
    #
    # @task(1)
    # def get_user_question_list(self):
    #     self.client.get("/user-questions/")
    #
    # @task(1)
    # def get_user_question_house_list(self):
    #     self.client.get("/user-questions/house/")

    # @task(1)
    # def post_create_house(self):
    #
    #     self.client.post("/houses/create", json={
    #         "title": "New House",
    #         "category": 6,
    #         "price": 100000,
    #         "purpose" : "Частный дом",
    #         "construction_technology": 1,
    #         "garage": False,
    #         "bedrooms": 2,
    #         "area": 120,
    #         "floors": 3,
    #         "rooms": 5
    #     })
    #
    # @task(1)
    # def update_house(self):
    #     house_id = choice([13, 14, 15])
    #     self.client.put(f"/houses/update/{house_id}/", json={
    #         "title": "Updated House",
    #         "price": 1200000
    #     })
