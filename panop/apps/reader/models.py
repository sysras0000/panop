from __future__ import unicode_literals

from django.db import models

from panop.apps.loader.models import Campaign, BatchData
from panop.apps.loader.utils import csv_to_kvp


class TestRun(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=False)
    data_file = models.ForeignKey(BatchData, on_delete=models.SET_NULL, null=True, blank=False)
    log_file = models.FileField(upload_to='logs/', null=True, blank=True)
    start = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=60)
    running = models.BooleanField(default=True)

    def get_data_file_rows(self, expanded=False, limited=False):
        if self.data_file.type == self.data_file.DELIMITED:
            return self.get_delimited_data_rows(expanded)
        elif self.data_file.type == self.data_file.CSV:
            return self.get_csv_data_rows(expanded, limited)

    def get_delimited_data_rows(self, expanded=False):
        config = self.campaign.get_config()
        self.data_file.data_file.open()
        rows = self.data_file.data_file.readlines()
        delimiter = config.get('campaign data map', 'delimiter')
        result = []
        if delimiter.lower() != 'fixed':
            key_dict = {int(index): col_name for index, col_name in config.items('campaign data map') if index.isdigit()}
            for row in rows:
                fields = row.decode("utf-8").split(delimiter)
                try:
                    result.append({col_name: fields[index] for index, col_name in key_dict.items()})
                except IndexError:
                    return ["Failed to parse rows", ]
        else:  # fixed-length fields
            # After the following line, field_positions should be a list of fields in the format
            # ([start, stop], name), e.g. 0-5: customer_id should become ([0, 5], 'customer_id')
            field_positions = [([int(i) for i in position.split("-")], field_name) for position, field_name
                               in config.items('campaign data map')
                               if position[0].isdigit()]
            for row in rows:
                result_row = {}
                for field in field_positions:
                    result_row[field[1]] = row.decode("utf-8")[field[0][0]:field[0][1]+1]
                result.append(result_row)
            delimiter = ", "  # Reset the delimiter for visual niceness
        return result if expanded else [delimiter.join(row.values()) for row in result]

    def get_csv_data_rows(self, expanded=False, limited=False):
        data = csv_to_kvp(self.data_file.data_file.path)
        if expanded and not limited:
            return data
        config = self.campaign.get_config()
        keys = [v for index, v in config.items('campaign data map') if index.isdigit()]
        relevant_data = [{k: v for k, v in row.items() if k in keys} for row in data]
        if not expanded:
            return [', '.join(row.values()) for row in relevant_data]
        return relevant_data