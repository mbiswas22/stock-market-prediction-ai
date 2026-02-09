from model.predict import predict_trend
 
def predict_tool(features):
    return predict_trend(features)
 
def explain_tool(chain, question):
    return chain.run(question)
