# a) To verify the signature provided by someone who claims to be Bob, we can use the rsa_signature_verify function with Bob's RSA public key (n, e).

# Let's first verify the original signature:


import hashlib

# Given message and signature
message = "Your checking account available balance is 12,617,290 dollars and 56 cents."
signature = 0x230e2ee7c95e6c1faae818682fa25f19d3148077de82a30c44618f397fb0309fc4fe545e6cda6c46dbe81aea4ad76cf3c6ed5066df1a6b1f187063d6cb3f8da69675e91cb9ffea6a79814bd27153f04cfd143d519f8ce0025cc1205c2472294343f14a2d041ddc3821359638638a96d58e6b99a904f6099eea9c74012dd64569

# Bob's RSA public key (n, e)
n = 0x97987cc9520bf98c049dd4fdd0b2ef50a8cd876bc89b3f43708a8d26e05a2923a312688cd2a50d8e01fa3e20181387d07e9b75d00ad07b2e302983cf16b56bb4dbeeeb2709a22053c44fc743abcac8fc8511b97062ac8c298feeebce70c6851a6752b4f27a8a0fbdd3b202e3e10ea48a912d31f96ecb7bf8fe86934a9b466b71
e = 0x10001

def rsa_message_sign(message: str, d: int, n: int) -> int:
    digest = hashlib.sha256(message.encode("ascii", "ignore"))
    return pow(int(digest.hexdigest(),16), d, n)
def rsa_signature_verify(message: str, signature: int, e: int, n: int) -> bool:
    expected_digest = pow(signature, e, n)
    digest = int(hashlib.sha256(message.encode("ascii", "ignore")).hexdigest(), 16)
    return expected_digest == digest


# Verify the signature
is_verified = rsa_signature_verify(message, signature, e, n)

print("a) ", end = "")
if is_verified:
    print("The signature is verified. It is likely from Bob.")
else:
    print("The signature is not verified. It may not be from Bob or the message has been tampered with.")


# b) Change the dollar amount in the message and try verifying the signature for the updated message. The signature will not be verified because even a small change in the message will result in a completely different hash value.

# Updated message with a different dollar amount
updated_message = "Your checking account available balance is 1,000,000 dollars."

# Verify the updated signature
is_verified_updated = rsa_signature_verify(updated_message, signature, e, n)

print("b) ", end = "")
if is_verified_updated:
    print("The updated signature is verified. It is likely from Bob.")
else:
    print("The updated signature is not verified. It may not be from Bob or the message has been tampered with.")

# c) To find the genuine signature for the updated message, we can use Bob's private key (n, d) and the rsa_message_sign function. We need to sign the updated message using Bob's private key:

# Bob's RSA private key (n, d)
d = 0x95e378e699902b826d021d99846397ca19cd75eb756342ef0c7481d2019c43f6ef83010ad42fcc322ff45cbee0ef56a728b7cf8a0f5749a4468c95bd29397427f3316bbfa4902bb8cc5a6ea572ff24368f17ff952c6965ffc1d5d467ce06fab9e87833fe3438d1a69cfdac2c4e20fa0f5793fdbc1057073d3dbb12f613d52b9d

# Sign the updated message
genuine_signature = rsa_message_sign(updated_message, d, n)
print("c) ", end = "")
print("Genuine Signature for the Updated Message:", hex(genuine_signature))
