# pymailclient

er is a python wrapper that can be used to send beautiful email in any python base application. it allow developers to pass in their html template and the wrapper will render it and send the beautiful template out the reciepient. It can also be used to send attachements with email sent to reciepient.

                                            DOCUMENTATION

INSTALLATION

We have to install the library into our virtual environment and we can do that by using the below command.

        pip install pymailclient

or

        pip3 install pymailclient


USAGE

After Installation, we need to create a directory in our project and name it "template" and then create another directory called "email" which will house all our html email files. ie

          project directory -> template -> email -> email html files


THEN

import all the functions

                      from email_client.pymail import clients, Email

Initiate the class

                      send = Email()

Supply all the SMTP credentials that will be used to send the email out.

                      credential = clients(
                            email_host='smtp.gmail.com',
                            email_port='587',
                            email_user='email',
                            email_pass='password',
                            email_protocol='TLS',
                            email_sender='sender'
                        )



Declare your HTML Template

                      html = 'templatename.html'

Load the HTML Template in the function and pass in the data you want to pass to the html template from python as a dictionary. 


                      template_data = send.load_template(html, {'name':'samson', 'amount':'1000'})

In the html template, you can now get the value of the data passed from python by using the the jinja2 pattern. ie 

                            {{name}} {{amount}}

            <!DOCTYPE html">
            <html xmlns="http://www.w3.org/1999/xhtml">
                  <h1>Hi {{name}},</h1>
                  <strong>Amount:</strong> {{amount}}
            </html>


Then we can now call the function to send the email by using the below function.

SEND WITHOUT ATTACHED FILE

                      send.sendEmail(
                        credential, 
                        template_data, 
                        receiver_email='reciever@gmail.com', 
                        subject="Python Test", 
                        bcc='test@gmail.com, test2@gmail.com'
                        )


SEND EMAIL WITH ATTACHED FILE

                      send.sendEmailWithFile(
                        credential, 
                        template_data, 
                        subject="Python Test", 
                        receiver_email='reciever@gmail.com',
                        pathToFile='path to file/Report.pdf', 
                        docName='test', 
                        bcc='test@gmail.com, test2@gmail.com'
                        )



FULL USAGE

                    from email_client.pymail import clients, Email

                    send = Email()

                    credential = clients(
                            email_host='smtp.gmail.com',
                            email_port='587',
                            email_user='email',
                            email_pass='password',
                            email_protocol='TLS',
                            email_sender='sender'
                        )
                      html = 'templatename.html'
                      template_data = send.load_template(html, {'name':'samson', 'amount':'1000'})

                    //Send without files/attachement //

                    send.sendEmail(
                        credential, 
                        template_data, 
                        receiver_email='reciever@gmail.com', 
                        subject="Python Test", 
                        bcc='test@gmail.com, test2@gmail.com'
                        )

                    

                    // Send with attachement //

                    send.sendEmailWithFile(
                        credential, 
                        template_data, 
                        subject="Python Test", 
                        receiver_email='reciever@gmail.com',
                        pathToFile='path to file/Report.pdf', 
                        docName='test', 
                        bcc='test@gmail.com, test2@gmail.com'
                        )

NOTE

If you dont want to use bcc, kindly set it to None. ie bcc=None. Also the email protocol must be either SSL or TLS depending the protocol you are using.
        