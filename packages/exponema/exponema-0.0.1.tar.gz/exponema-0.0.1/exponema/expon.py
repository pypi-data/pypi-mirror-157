def ex(value,degree):
    if (isinstance(value,int)==True) and (isinstance(degree,int)==True):
        result = int(value) ** int(degree)
        return result
    
    else:
        response = "Value and Degree must be integers"
        return response
    