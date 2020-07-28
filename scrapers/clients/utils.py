def get_date_from_archive(date, archive, date_field_name="Data"):
    for item in archive:
        if item[date_field_name] == date:
            return item
