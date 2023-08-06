import argparse

from rcn import configure, profile

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("actions", nargs='*', type=str)
    parser.add_argument("--profile",default="default", help="configure a specific profile. Default - default")
    namespace = parser.parse_args()
    profile_name = namespace.profile
    actions = namespace.actions

    if actions[0] == "configure":
        configure(profile=profile_name)
    if actions[0] == "profile":
        profile(actions[1:])

    # configure("admin", "admin", "http://localhost:8080/backend", "default")