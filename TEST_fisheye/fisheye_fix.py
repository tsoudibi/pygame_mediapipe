import cv2
import numpy as np
import glob

# active camera, use cv2 rather then pygame
camera = cv2.VideoCapture(0)
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
camera.set(cv2.CAP_PROP_FRAME_WIDTH, SCREEN_WIDTH)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_HEIGHT)

def get_K_and_D(checkerboard):

    CHECKERBOARD = checkerboard
    subpix_criteria = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
    calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC+cv2.fisheye.CALIB_CHECK_COND+cv2.fisheye.CALIB_FIX_SKEW
    objp = np.zeros((1, CHECKERBOARD[0]*CHECKERBOARD[1], 3), np.float32)
    objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
    _img_shape = None
    objpoints = []
    imgpoints = []
    images = glob.glob( 'pygame_mediapipe/TEST_fisheye/photos/*.jpg')
    for fname in images:
        img = cv2.imread(fname)
        if _img_shape == None:
            _img_shape = img.shape[:2]
        else:
            assert _img_shape == img.shape[:2], "All images must share the same size."

        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD,cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
        if ret == True:
            objpoints.append(objp)
            cv2.cornerSubPix(gray,corners,(3,3),(-1,-1),subpix_criteria)
            imgpoints.append(corners)
    N_OK = len(objpoints)
    K = np.zeros((3, 3))
    D = np.zeros((4, 1))
    rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
    tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
    rms, _, _, _, _ = cv2.fisheye.calibrate(
        objpoints,
        imgpoints,
        gray.shape[::-1],
        K,
        D,
        rvecs,
        tvecs,
        calibration_flags,
        (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
    )
    DIM = _img_shape[::-1]
    print("Found " + str(N_OK) + " valid images for calibration")
    print("DIM=" + str(_img_shape[::-1]))
    print("K=np.array(" + str(K.tolist()) + ")")
    print("D=np.array(" + str(D.tolist()) + ")")
    return DIM, K, D


def undistort(K,D,DIM,scale=0.6,imshow=False):
    while True:
        success, img = camera.read()
        dim1 = img.shape[:2][::-1]  #dim1 is the dimension of input image to un-distort
        assert dim1[0]/dim1[1] == DIM[0]/DIM[1], "Image to undistort needs to have same aspect ratio as the ones used in calibration"
        if dim1[0]!=DIM[0]:
            img = cv2.resize(img,DIM,interpolation=cv2.INTER_AREA)
        Knew = K.copy()
        if scale:#change fov
            Knew[(0,1), (0,1)] = scale * Knew[(0,1), (0,1)]
        map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), Knew, DIM, cv2.CV_16SC2)
        undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        if imshow:
            img_valid, ratio = cut(undistorted_img)
            print (img_valid.shape)
            cv2.imshow("undistorted", img_valid)
        if cv2.waitKey(5) & 0xFF == 27:
                break
    #return undistorted_img



def cut(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    (_, thresh) = cv2.threshold(img_gray, 20, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(contours, key=cv2.contourArea, reverse=True)[0]
    x,y,w,h = cv2.boundingRect(cnts)
    ratio = 1.2
    x = int(x + w/2 - ratio*1280/2)
    y = int(y + h/2 - ratio*720/2)
    w = int(1280 * ratio)
    h = int(720 * ratio)
    print(x,y,w,h)
    r = max(w/ 2, h/ 2)
    img_valid = img[y:y+h, x:x+w]
    return img_valid, int(r)

if __name__ == '__main__':

    DIM, K, D = get_K_and_D((6,9))
    undistort(K,D,DIM,imshow= True)

    '''
    DIM=(2560, 1440)
    K=np.array([[1694.7801205342007, 0.0, 1363.235424743914], [0.0, 1694.4106664109822, 686.0493220616949], [0.0, 0.0, 1.0]])
    D=np.array([[-0.010547721322285927], [0.02576312669611254], [-0.1546810103404629], [0.15853057545495458]])
    x,y,w,h = 475,254,1536,864
    '''
# Quote from https://medium.com/@kennethjiang/calibrate-fisheye-lens-using-opencv-333b05afa0b0
# Quote from https://blog.csdn.net/donkey_1993/article/details/103909811