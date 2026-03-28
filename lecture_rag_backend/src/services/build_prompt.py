def build_prompt(instructions,  query):
	msgs = []
	msgs.append({"role": "system", "content": instructions})
	msgs.append({"role": "user", "content": query})
	return msgs
