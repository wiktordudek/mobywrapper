import time

import mobywrapper


def call_to_action(code: int) -> None:
    print(f"⚡ Show the code to the person you’re verifying the documents for. ")
    print(
        f"📲 When that person enters the code, you’ll see their details on your screen."
    )
    print(f"🔢 Code: {code}\n")


def person_pretty_print(person: mobywrapper.Person) -> None:
    print("\n✅ mDowód has been verified.")
    print()
    print(f"👤 Nazwisko: {person.surname}\t👤 Imię (imiona): {person.names}")
    print(f"🔢 Number PESEL: {person.pesel}\t👶🏻 Data urodzenia: {person.birth_date}")
    print(
        f"🌐 Obywatelstwo: {person.citizenship}\t🧔🏻 Imię ojca: {person.father_name}"
    )
    print(
        f"👩🏻 Imię matki: {person.mother_name}\t🪪 Seria i nr dokumentu mDowód: {person.eid_number}"
    )
    print()
    print(f"🪪 Data wydania dokumentu mDowód: {person.eid_issue_date}")
    print(f"🪪 Termin ważności dokumentu mDowód: {person.eid_expiry_date}")
    print()


def start_fetching(
    processor: mobywrapper.VerificationProcessor,
) -> mobywrapper.Person | None:
    max_time = 180
    retry_time = 5

    for _ in range(1, max_time // retry_time + 1):
        time.sleep(retry_time)
        encrypted_person = processor.fetch_data()
        if not encrypted_person:
            print(f"❌ No data received. Retrying in 5 seconds.")
            continue

        person: mobywrapper.Person = encrypted_person.decrypt(processor.keypair)
        return person

    return None


def main():
    processor = mobywrapper.VerificationProcessor()

    app_prompt = processor.begin()
    call_to_action(app_prompt.code)

    person = start_fetching(processor)

    if person:
        person_pretty_print(person)
    else:
        print(f"❌ Code expired.")


if __name__ == "__main__":
    main()
