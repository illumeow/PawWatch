"""Today vs the 7-day baseline. Owner: B. Reads only through store.

Wording suggests watching or seeing a vet; never a diagnosis.
"""


def find_anomalies(conn, today=None):
    """Zones whose count today differs a lot from the previous 7-day mean."""
    raise NotImplementedError  # TODO(B)
