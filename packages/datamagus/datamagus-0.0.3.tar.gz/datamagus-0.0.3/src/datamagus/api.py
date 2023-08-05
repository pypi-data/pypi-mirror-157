from flask import Flask, request
from flasgger import Swagger, LazyString, LazyJSONEncoder

## app
app = Flask(__name__)
app.json_encoder = LazyJSONEncoder

## swagger
swagger_template = dict(
    info = {
        'title': LazyString(lambda: 'DataMagus UI document'),
        'version': LazyString(lambda: '0.0.1'),
        'description': LazyString(lambda: 'API interface for basic data analysis\
         processing, graphing and modeling, and practical use.'),
        },
        host = LazyString(lambda: request.host)
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'alazia',
            "route": '/alazia.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}
swagger = Swagger(app, template=swagger_template,             
                  config=swagger_config)

## api v0.0.1
@app.route("/",methods=['post'])
def hello_world():
    """
    This is the human_brain_heatmap API
    Call this api passing a json and get back its features
    ---
    tags:
      - Human_brain_heatmap API
    parameters:
      - name: targetTissue
        in: query
        type: string
        required: true
        description: targetTissue
      - name: compareTissue
        type:  string
        required: true
        description: compareTissue
      - name: pValuePar
        type:  double
        required: true
        description: pvalue-cutoff
      - name: folChaPar
        type:  double
        required: true
        description: foldchange-cutoff
    responses:
      200:
        description: success
    """
    return "Hello World!!!"

if __name__ == '__main__':
    app.run()