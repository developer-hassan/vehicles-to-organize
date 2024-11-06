from agent import LangchainAgent
import json


def main():
    # Define valid family names and descriptions
    valid_names = ["M1", "M2", "R", "M", "C", "Cs", "SERIES 1", "M3", "A30", "Mini", "Cooper", "A35", "430", "Q", "CRV",
                   "CRX", "F360", "25/30HP"]
    descriptions = [
        "1990 BMW M1E805",
        "1982 BMW 633 Csi",
        "2001 BMW R1100S",
        "2001 BMW Constant ETC",
        "2001 BMW M3 Coupe",
        "2001 Bmw Sabrio 330Ci",
        "1957 Austin Somerset A 35",
        "14k Mile 2006 Ferrari F430 Spider 6 Speed Conversion",
        "14k Mile 2006 Mini Copper S F430 Spider 6 Speed Conversion",
        "1974 Honda QA50",
        "1983 Honda CR80R",
        "21k Mile 2003 Ferrari 360 Modena",
        "1933 Rolls Royce 25/30"
    ]

    # Create an instance of LangchainAgent
    agent = LangchainAgent(valid_names, descriptions)

    # Get the response from the agent
    response = agent.get_response()

    # Print the response
    print(response.content)

    with open("test.json", "w") as test_ai_file:
        json.dump({"output": response.content}, test_ai_file)


if __name__ == "__main__":
    main()
