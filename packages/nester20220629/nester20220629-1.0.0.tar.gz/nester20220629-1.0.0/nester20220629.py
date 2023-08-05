a = ["a","b","c",["h","i","j",["o","p",["r","s","t","u","v","w","x"],"q"],"k","l","m","n"],"d","e","f","g"]
def print_lol(the_list):
	for i in the_list:
		if isinstance(i,list):
			print_lol(i)
		else:
			print(i)