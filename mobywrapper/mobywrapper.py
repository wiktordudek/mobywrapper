"""mObywrapper.

a Python module that replicates the functionality of the
official Polish eID verificator website: https://weryfikator.mobywatel.gov.pl/

"""

from base64 import b64decode, b64encode
from json import loads
from uuid import uuid4

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from .constants import EID_DATA_PULL, EID_START, LEGIT_BROWSER_HEADERS


class RSAKeyPair:
    """A class representing an RSA key pair.

    Attributes:
        private_key (rsa.PrivateKey): The private key of the RSA key pair.
        public_key (rsa.PublicKey): The public key of the RSA key pair.

    Methods:
        __init__: Initializes a new RSA key pair with default settings.
        encode_base64_der: Returns the public key in base64-encoded DER format.

    """

    def __init__(self) -> None:  # noqa: D107
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()

        self.private_key = private_key
        self.public_key = public_key

    def encode_base64_der(self) -> str:
        """Return the public key in base64-encoded DER format.

        Returns:
            str: The base64-encoded public key as a string.

        """
        der = self.public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return b64encode(der).decode()


class AppPrompt:
    """Represents a prompt data shown to the user (number code and QR code).

    Attributes:
        code (int): The code that user can to enter in the app.
        qr_code (str): The QR code that user can to scan in the app.

    """

    def __init__(self, **kwargs) -> None:
        self.code: int = kwargs["code"]
        self.qr_code: str = kwargs["qrCode"]


class Person:
    """Represents an individual person with their personal and identification details.

    Attributes:
        picture (str): Base64-encoded picture of the person.
        surname (str): Surname of the person.
        names (str): Names of the person.
        pesel (str): Polish Personal Identification Number (PESEL) of the person.
        birth_date (str): Date of birth of the person.
        citizenship (str): Citizenship of the person.
        father_name (str): Father's name of the person.
        mother_name (str): Mother's name of the person.
        mobile_id_number (str): Mobile ID Card Number of the person.
        mobile_id_issue_date (str): Issue date of the Mobile ID Card of the person.
        mobile_id_expiry_date (str): Expiry date of the Mobile ID Card of the person.

    Args:
        **kwargs: Keyword arguments for the class attributes.

    """

    def __init__(self, verification_date: str, **kwargs) -> None:
        self.verification_date = verification_date
        self.picture: str = kwargs["picture"]
        self.surname: str = kwargs["surname"]
        self.names: str = kwargs["names"]
        self.pesel: str = kwargs["pesel"]
        self.birth_date: str = kwargs["birthDate"]
        self.citizenship: str = kwargs["citizenship"]
        self.father_name: str = kwargs["fatherName"]
        self.mother_name: str = kwargs["motherName"]
        self.mobile_id_number: str = kwargs["mobileIdCardNumber"]
        self.mobile_id_issue_date: str = kwargs["mobileIdCardValidFrom"]
        self.mobile_id_expiry_date: str = kwargs["mobileIdCardValidTo"]


class EncryptedPerson:
    """Represents an encrypted person data received from the API.

    Attributes:
        encrypted_data (str): Base64 encoded encrypted data.
        data_encryption_iv (str): Base64 encoded initialization vector for data encryption.
        data_encryption_algorithm (str): Data encryption algorithm used. Appears to always be "AES/CBC/PKCS5Padding".
        key_encryption_algorithm (str): AES key encryption algorithm used. Appears to always be "RSA/ECB/OAEPwithSHA-256andMGF1Padding".
        encrypted_encryption_key (str): Base64 encoded encrypted key for data decryption.
        verification_date (str): Date of verification. Example: "2025-01-01T00:00:00Z".

    Methods:
        decrypt: Decrypts the person object. Returns a Person object.

    """

    def __init__(self, **kwargs) -> None:
        # Our RSA-encrypted AES
        self.encrypted_encryption_key = kwargs["encryptedEncryptionKey"]
        self.key_encryption_algorithm = kwargs["keyEncryptionAlgorithm"]

        # Person's data encrypted with AES key
        self.encrypted_data = kwargs["encryptedData"]
        self.data_encryption_iv = kwargs["dataEncryptionIv"]
        self.data_encryption_algorithm = kwargs["dataEncryptionAlgorithm"]

        # Plain text data
        self.verification_date = kwargs["verificationDate"]

    def _extract_aes_key(self, private_key: rsa.RSAPrivateKey) -> bytes:
        encrypted_aes_key = b64decode(self.encrypted_encryption_key)
        return private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    def _decrypt_person_data(self, aes_key: bytes) -> str:
        raw_encrypted_data: bytes = b64decode(self.encrypted_data)
        raw_encryption_iv: bytes = b64decode(self.data_encryption_iv)

        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.CBC(raw_encryption_iv),
        )

        decryptor = cipher.decryptor()

        decrypted_data = decryptor.update(raw_encrypted_data) + decryptor.finalize()

        return decrypted_data.decode()

    def decrypt(self, rsa_keypair: RSAKeyPair) -> Person:
        """Decrypt the person object.

        Args:
            rsa_keypair (RSAKeyPair): Key pair for RSA decryption.

        Returns:
            Person: Decrypted person object.

        """
        aes_key: bytes = self._extract_aes_key(rsa_keypair.private_key)
        person_json: str = self._decrypt_person_data(aes_key)

        # For some reason gov.pl adds null character at the end of person's json 💀
        person_json = person_json.strip("\x01")

        data: dict = loads(person_json)
        return Person(
            self.verification_date,
            **data,
        )


class IDServerUnexpectedResponseError(Exception):
    """Raised when an unexpected response is received from the Mobile ID API.

    Args:
        status_code (int): The HTTP status code received in the response.

    """

    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        super().__init__()


class VerificationProcessor:
    """Manages the verification process.

    This processor is responsible for creating a new session, creating an RSA key pair,
    sending a request to start the verification flow, and pulling the person's data.

    """

    def __init__(self) -> None:
        self.session_uuid: uuid4 = uuid4()
        self.keypair: RSAKeyPair = RSAKeyPair()
        self.secret: None | str = None

    def begin(self) -> AppPrompt:
        """Start the verification flow.

        Sends a POST request to initiate the verification process.

        Returns:
            AppPrompt: The prompt to be displayed on the screen.

        """
        if self.secret is not None:
            message = "Cannot re-use the same VerificationProcessor"
            raise ValueError(message)

        payload = {
            "sessionUuid": str(self.session_uuid),
            "publicKey": {
                "encoded": self.keypair.encode_base64_der(),
                "algorithm": "RSA",
            },
        }

        response = requests.post(
            EID_START,
            json=payload,
            headers=LEGIT_BROWSER_HEADERS,
            timeout=10,
        )

        if (status_code := response.status_code) != requests.codes.ok:
            raise IDServerUnexpectedResponseError(status_code)

        result = response.json()
        self.save_secret(result)

        return AppPrompt(**result)

    def save_secret(self, result: dict) -> None:
        """Save the secret key obtained from the server during the verification flow.

        It is needed for later data fetching.

        """
        self.secret = result["secret"]

    def fetch_data(self) -> EncryptedPerson | None:
        """Fetch person's data related to this verification session.

        Returns:
            EncryptedPerson: Encrypted person's data to be decrypted
            or None if the session has expired or no data
            is available (user didn't enter the code in the app)

        """
        payload = {
            "secret": self.secret,
            "publicKey": {
                "encoded": self.keypair.encode_base64_der(),
                "algorithm": "RSA",
            },
        }
        response = requests.post(
            EID_DATA_PULL.format(session_uuid=str(self.session_uuid)),
            json=payload,
            headers=LEGIT_BROWSER_HEADERS,
            timeout=10,
        )

        sc = response.status_code

        if sc == requests.codes.no_content:
            return None

        if sc == requests.codes.ok:
            return EncryptedPerson(**response.json())

        raise IDServerUnexpectedResponseError(sc)
