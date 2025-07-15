from time import sleep

import mobywrapper

# Initialize verification processor
processor = mobywrapper.VerificationProcessor()

# Start a new verification session
app_prompt = processor.begin()
print(f"Enter this code in the app: {app_prompt.code}")

# Let the user enter the code in the mobile app
sleep(30)

# Fetch the data
encrypted_person = processor.fetch_data()
if encrypted_person:
    person = encrypted_person.decrypt(processor.keypair)
    print(f"Hi there, {person.names}!")
else:
    print("No data received.")
