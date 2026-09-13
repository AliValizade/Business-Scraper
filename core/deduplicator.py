class Deduplicator:
    """
    Detects duplicate businesses using a prioritized matching strategy:

    1. source + source_id
    2. normalized phone
    3. normalized name + normalized address
    """

    def find_duplicate(self, business, existing_businesses):
        """
        Find the first existing business that matches the given business.

        Returns:
            The matching business dictionary, or None.
        """

        if not isinstance(business, dict):
            raise TypeError(
                "Business data must be a dictionary."
            )

        for existing in existing_businesses:
            if self._match_source_id(
                business,
                existing,
            ):
                return existing

        for existing in existing_businesses:
            if self._match_phone(
                business,
                existing,
            ):
                return existing

        for existing in existing_businesses:
            if self._match_name_address(
                business,
                existing,
            ):
                return existing

        return None

    def is_duplicate(self, business, existing_businesses):
        """
        Return True if the business matches an existing business.
        """

        return (
            self.find_duplicate(
                business,
                existing_businesses,
            )
            is not None
        )

    def deduplicate(self, businesses):
        """
        Remove duplicates from a list of business dictionaries.

        The first occurrence is kept.
        """

        unique_businesses = []
        duplicates = []

        for business in businesses:
            duplicate = self.find_duplicate(
                business,
                unique_businesses,
            )

            if duplicate is not None:
                duplicates.append(business)
                continue

            unique_businesses.append(business)

        return unique_businesses, duplicates

    def _match_source_id(self, business, existing):
        source = business.get("source")
        source_id = business.get("source_id")

        existing_source = existing.get("source")
        existing_source_id = existing.get("source_id")

        if not source or not source_id:
            return False

        if not existing_source or not existing_source_id:
            return False

        return (
            source == existing_source
            and source_id == existing_source_id
        )

    def _match_phone(self, business, existing):
        phone = business.get("phone")
        existing_phone = existing.get("phone")

        if not phone or not existing_phone:
            return False

        return phone == existing_phone

    def _match_name_address(self, business, existing):
        name = business.get("name")
        address = business.get("address")

        existing_name = existing.get("name")
        existing_address = existing.get("address")

        if not name or not address:
            return False

        if not existing_name or not existing_address:
            return False

        return (
            name == existing_name
            and address == existing_address
        )