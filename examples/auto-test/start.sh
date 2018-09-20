echo "Run with parameter ci/release/normal!"
if [ ! -d "pai/" ]; then
    git clone -b yuqian/examples_fix https://github.com/Microsoft/pai.git
    mv pai/examples/ . && rm -rf pai/
    if [ $1 == "ci" ]; then
        threshold=10
    elif [ $1 == "release" ]; then
        threshold=60
    else
        threshold=30
    fi
    full="cntk-mpi,tensorflow-mpi,sklearn-mnist,sklearn-text-vectorizers,tensorflow-cifar10,tensorflow-tensorboard,tensorflow-distributed-cifar10,kafka,mxnet-image-classification,mxnet-autoencoder,jupyter_example,tensorflow-serving,xgboost_gpu_hist,cntk-g2p,keras_cntk_backend_mnist,keras_tensorflow_backend_mnist,caffe-mnist,pytorch-regression,pytorch-mnist,chainer-cifar,caffe2-resnet50"
    stable="sklearn-text-vectorizers,tensorflow-tensorboard,tensorflow-distributed-cifar10,kafka,mxnet-image-classification,jupyter_example,tensorflow-serving,xgboost_gpu_hist,cntk-g2p,keras_tensorflow_backend_mnist,caffe-mnist,pytorch-regression,pytorch-mnist,caffe2-resnet50"
    echo "If the sklearn-mnist, keras_cntk_backend_mnist, keras_tensorflow_backend_mnist, mxnet-autoencoder or tensorflow-cifar10 job failed, it may due to the official data downloading source being unstable. Just try again!"
    read -p "Please input name of the examples you want to run with ',' between two names, or you can just input F/S to run full jobs or only stable jobs:" mode
    if [ $mode == "F" ]; then
        jobs=$full
    elif [ $mode == "S" ]; then
        jobs=$stable
    else
        jobs=$mode
    fi
    abspath=`pwd`/pai_tmp/examples/auto-test
    python3 $abspath/start_all_test.py --path ./examples --threshold $threshold --rest_server_socket $2 --hdfs_socket $3 --webhdfs_socket $4 --PAI_username $5 --PAI_password $6 --jobs $jobs
    rm -rf ./examples/
else
    echo "Pai folder already exist! Please remove it or run this project in another folder!"
fi