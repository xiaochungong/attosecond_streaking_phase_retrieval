import tensorflow as tf
import crab_tf2
xuv_time_domain_func = crab_tf2.xuv_time_domain
import network2
import unsupervised
import matplotlib.pyplot as plt
import numpy as np
import scipy.constants as sc


def create_plots():

    fig = plt.figure(figsize=(10,6.5))
    gs = fig.add_gridspec(2,4)

    axes = {}

    axes['input_image'] = fig.add_subplot(gs[0,0:3])
    axes['input_xuv_time'] = fig.add_subplot(gs[0,3])
    # axes['input_xuv'] = fig.add_subplot(gs[0,1])
    # axes['input_ir'] = fig.add_subplot(gs[0,0])

    axes['generated_image'] = fig.add_subplot(gs[1,0:3])
    axes['predicted_xuv_time'] = fig.add_subplot(gs[1, 3])
    # axes['predicted_xuv'] = fig.add_subplot(gs[2, 1])
    # axes['predicted_ir'] = fig.add_subplot(gs[2, 0])

    # add time plots

    return axes



def update_plots(generated_image, input_image, actual_fields, predicted_fields):

    # set phase angle to 0
    # find angle 0
    index_0_angle = 25
    #plt.figure(999)
    #plt.plot(np.real(actual_fields['xuv_f']), color='blue')
    #plt.plot(np.imag(actual_fields['xuv_f']), color='red')
    #plt.plot(np.unwrap(np.angle(actual_fields['xuv_f'])), color='green')
    #plt.plot([index_0_angle,index_0_angle], [-1, 1])
    #plt.ioff()
    #plt.show()
    xuv_actual_time = sess.run(xuv_time_domain_func, feed_dict={crab_tf2.xuv_cropped_f: actual_fields['xuv_f']})
    xuv_predicted_time = sess.run(xuv_time_domain_func, feed_dict={crab_tf2.xuv_cropped_f: predicted_fields['xuv_f']})


    # set phase angle to 0
    predicted_fields['xuv_f'] = predicted_fields['xuv_f'] * np.exp(-1j * np.angle(predicted_fields['xuv_f'][index_0_angle]))

    iteration = i+1

    # calculate loss
    loss_value = sess.run(network2.u_losses, feed_dict={network2.x: trace})
    print('iteration: {}'.format(iteration))
    print('loss_value: ', loss_value)

    xuv_t_vals_si = crab_tf2.xuv.tmat * sc.physical_constants['atomic unit of time'][0]
    axes['input_xuv_time'].cla()
    axes['input_xuv_time'].text(0.0, 1.05, 'Actual XUV E(t)', transform=axes['input_xuv_time'].transAxes, backgroundcolor='white')
    axes['input_xuv_time'].plot(xuv_t_vals_si*1e18, np.real(xuv_actual_time), color='blue', alpha=0.5)
    axes['input_xuv_time'].plot(xuv_t_vals_si*1e18, np.abs(xuv_actual_time), color='black')
    axes['input_xuv_time'].set_xlabel("time [as]")
    axes['input_xuv_time'].set_ylabel("Electric Field [arbitrary units]")
    axes['input_xuv_time'].yaxis.tick_right()
    axes['input_xuv_time'].yaxis.set_label_position("right")
    axes['input_xuv_time'].set_yticks([0.02, 0.01, 0, -0.01, -0.02])


    axes['input_image'].cla()
    tauvalues_si = crab_tf2.tau_values * sc.physical_constants['atomic unit of time'][0]
    axes['input_image'].pcolormesh(tauvalues_si*1e15, crab_tf2.p_values, input_image, cmap='jet')
    axes['input_image'].text(0.0, 1.05, 'Input Streaking Trace', transform=axes['input_image'].transAxes, backgroundcolor='white')
    axes['input_image'].set_ylabel("momentum [atomic units]")
    axes['input_image'].set_xlabel("delay [fs]")


    axes['predicted_xuv_time'].cla()
    axes['predicted_xuv_time'].text(0.0, 1.05, 'Predicted XUV E(t)', transform=axes['predicted_xuv_time'].transAxes,
                                backgroundcolor='white')
    axes['predicted_xuv_time'].plot(xuv_t_vals_si*1e18, np.real(xuv_predicted_time), color='blue', alpha=0.5, label='Real E(t)')
    axes['predicted_xuv_time'].plot(xuv_t_vals_si*1e18, np.abs(xuv_predicted_time), color='black', label='|E(t)|')
    axes['predicted_xuv_time'].set_xlabel("time [as]")
    axes['predicted_xuv_time'].set_ylabel("Electric Field [arbitrary units]")
    axes['predicted_xuv_time'].legend(bbox_to_anchor=(0.5, -0.4), ncol=2, loc='center')
    #axes['predicted_xuv_time'].legend(loc=4)
    axes['predicted_xuv_time'].yaxis.tick_right()
    axes['predicted_xuv_time'].yaxis.set_label_position("right")
    axes['predicted_xuv_time'].set_yticks([0.02, 0.01, 0, -0.01, -0.02])



    axes['generated_image'].cla()
    axes['generated_image'].pcolormesh(tauvalues_si*1e15, crab_tf2.p_values, generated_image, cmap='jet')
    axes['generated_image'].text(0.0, 1.05, 'Generated Streaking Trace', transform=axes['generated_image'].transAxes, backgroundcolor='white')
    #axes['generated_image'].text(0.0, 1.0, 'iteration: {}'.format(iteration), transform = axes['generated_image'].transAxes, backgroundcolor='white')

    axes['generated_image'].text(0.1, 0.1, 'MSE: {}'.format(str(loss_value)),
                                 transform=axes['generated_image'].transAxes, backgroundcolor='white')
    axes['generated_image'].set_ylabel("momentum [atomic units]")
    axes['generated_image'].set_xlabel("delay [fs]")

    # save image
    # dir = "./nnpictures/unsupervised/" + modelname + "/" + run_name + "/"
    # if not os.path.isdir(dir):
    #     os.makedirs(dir)
    # plt.savefig(dir + str(iteration) + ".png")


    plt.subplots_adjust(left=0.08, right=0.92, hspace=0.4, wspace=0.3, bottom=0.18)
    plt.show()




def generate_images_and_plot():
    # generate an image from the input image
    generated_image = sess.run(network2.image, feed_dict={network2.x: trace})
    trace_2d = trace.reshape(len(crab_tf2.p_values), len(crab_tf2.tau_values))
    predicted_fields_vector = sess.run(network2.y_pred, feed_dict={network2.x: trace})

    predicted_fields = {}
    predicted_fields['xuv_f'], predicted_fields['ir_f'] = network2.separate_xuv_ir_vec(predicted_fields_vector[0])

    # plot the trace and generated image
    update_plots(generated_image, trace_2d, actual_fields, predicted_fields)



if __name__ == "__main__":

    i = 0


    # make unsupervised learning plot
    modelname = 'unsupervised_highres'

    # get the trace
    trace, actual_fields = unsupervised.get_trace(index=2, filename='attstrace_test2_processed.hdf5')

    # create plot axes
    axes = create_plots()

    with tf.Session() as sess:



        saver = tf.train.Saver()
        saver.restore(sess, './models/{}.ckpt'.format(modelname+'_unsupervised'))

        generate_images_and_plot()











