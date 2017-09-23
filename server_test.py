from flask import Flask,request,make_response
import dump

app = Flask(__name__,static_folder='.',static_url_path='')


@app.route('/echo/<thing>')
def echo(thing):
    return 'hello %s' % thing

if __name__ == '__main__':

    # dump.update()

    app.run(host='0.0.0.0',port=9998,debug=False)

    # dump.update_flag = False

    print('called here')

