if __name__ == "__main__":

    print("Generating Candidates...")

    candidates = generate_fake_candidates(20)

    print("Generating Sessions...")

    sessions = generate_exam_sessions(candidates)

    print("Generating Event Logs...")

    generate_event_logs(sessions)

    print("Done!")