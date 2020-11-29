import os

from endpoint_collection import EndpointCollection
from endpoints import ENDPOINT_COLLECTIONS

DIRECTORY = "daemon/endpoints"


# noinspection PyProtectedMember
def build_collection(collection: EndpointCollection):
    print(f"Building collection '{collection._name}'")
    with open(os.path.join(DIRECTORY, collection._name + ".rst"), "w") as file:
        file.write(f".. currentmodule:: endpoints.{collection._name}\n\n")

        title = f"{collection._name.capitalize()} Endpoints"
        file.write(f"{title}\n{'='*len(title)}\n\n")

        file.write(collection._description + "\n\n")

        for endpoint in collection._endpoints.values():
            print(f"  {endpoint.path}")

            title = f"`{endpoint._name}`"
            file.write(f"{title}\n{'-' * len(title)}\n\n")

            file.write(f".. admonition:: Path\n\n    `{endpoint.path}`\n\n")

            file.write(f".. autofunction:: {endpoint._func.__name__}\n\n")

        file.flush()


def main():
    if not os.path.exists(DIRECTORY):
        os.mkdir(DIRECTORY)

    for collection in ENDPOINT_COLLECTIONS:
        build_collection(collection)


if __name__ == "__main__":
    main()
