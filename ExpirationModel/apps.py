from __future__ import unicode_literals
from django.apps import AppConfig
import requests
import json
import pickle
from datetime import datetime


# class ExpirationmodelConfig(AppConfig):
#     name = 'ExpirationModel'


class Data(AppConfig):
    name = 'ExpirationModel'
    forest = pickle.load(open("./static/forest.pkl", "rb"))
    vectorizer = pickle.load(open("./static/vectorizer.pkl",
                                  "rb"))
    thresholds = [0.075, 0.3, 0.7, 0.8, 0.9, 0.95, 1]
    threshold_info = {0.075: {'percentage_expired': 75.4,
                                   'category': 7},
                           0.3: {'percentage_expired': 53.6,
                                 'category': 6},
                           0.7: {'percentage_expired': 37.3,
                                 'category': 5},
                           0.8: {'percentage_expired': 25.8,
                                 'category': 4},
                           0.9: {'percentage_expired': 16.3,
                                 'category': 3},
                           0.95: {'percentage_expired': 8.8,
                                  'category': 2},
                           1: {'percentage_expired': 1.0,
                               'category': 1}}

    @staticmethod
    def predict(features):
        features = Data.vectorizer.transform(features)
        prediction = Data.forest.predict_proba(features)[0][1]
        for threshold in Data.thresholds:
            if prediction < threshold:
                return Data.threshold_info[threshold]
        return Data.threshold_info[1]

    @staticmethod
    def get_loans(loanid):
        """
        Pulls and returns data about specific loans from the Kiva API.
        Includes a time sleep to ensure that usage limits aren't exceeded.
        No more than 100 loan ID
        :param loanid:
        :return loans:
        """
        response = requests.get(
            "http://api.kivaws.org/v1/loans/" + loanid + ".json",
            params={"appid": "com.woodside.autotag"})
        loan = json.loads(response.text)["loans"][0]
        return loan

    @staticmethod
    def preprocess_loan(loan):
        result = {}
        date = datetime.strptime(loan["planned_expiration_date"],
                                 "%Y-%m-%dT%H:%M:%SZ")
        result["day"] = date.day
        result["partner"] = Data.get_partner_name(loan["partner_id"])
        for item in ["sector", "activity", "loan_amount"]:
            result[item] = loan[item]
        result["country"] = loan["location"]["country"]
        result["total_borrowers_count"] = len(loan["borrowers"])
        numFemale = 0
        for borrower in loan["borrowers"]:
            if borrower["gender"] == "F":
                numFemale += 1
        result["percent_female"] = float(numFemale) / result[
            "total_borrowers_count"]
        result["loan_term_in_months"] = loan["terms"]["repayment_term"]
        return result

    @staticmethod
    def get_partner_name(partner_id):
        response = requests.get(
            "http://api.kivaws.org/v1/partners/" + str(partner_id) +
                ".json",
            params={"appid": "com.woodside.autotag"})
        return json.loads(response.text)["partners"][0]["name"]

    @staticmethod
    def do_everything(loanid):
        loan = Data.get_loans(loanid)
        features = Data.preprocess_loan(loan)
        return Data.predict(features)
