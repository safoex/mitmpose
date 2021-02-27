from mitmpose.routines.test.inference.next_pose_check import *
import sys

testclass = 'melpollo'
panda_dir = "/home/safoex/Documents/data/aae/panda_data_10_02_2021/%s/%s_0/rad_0.35" % (testclass, testclass)

device = torch.device('cuda:0')
classes = {'babyfood': ['meltacchin', 'melpollo'],
           'babymilk': ['humana1', 'humana2']}

models_dir = '/home/safoex/Documents/data/aae/models/scans/'
models_names = ['meltacchin', 'melpollo', 'humana1', 'humana2']
models = {mname: {'model_path': models_dir + '/' + mname + '.obj', 'camera_dist': None} for mname in models_names}

recorded_data_dir = panda_dir

if __name__ == "__main__":
    fr = FakeResponse(recorded_data_dir)


    n_exps = int(sys.argv[1])

    # grider = Grid(100, 5)
    grider = Grid(300, 20)
    ds = HierarchicalManyObjectsDataset(grider, models, res=236,
                                        classification_transform=HierarchicalManyObjectsDataset.transform_normalize,
                                        aae_render_transform=AAETransform(0.5,
                                                                          '/home/safoex/Documents/data/VOCtrainval_11-May-2012',
                                                                          add_patches=False, size=(236, 236)))

    nipple = NextPoseProvider(workdir, ds, fr.traj.rots, device, classes, fr=fr)
    nipple.load_everything("", "")
    nipple.load_or_render_codebooks()

    av_test_dir = panda_dir + '/av_test_%d/' % n_exps

    exp_dir_pattern = av_test_dir + 'exp_%d/'

    jump_limit = 5
    tests = 10
    ambiguity = 1
    tabs = ''


    for t in range(tests):
        initial_class = None
        final_class = None
        j = 0

        image_pattern = exp_dir_pattern % t + '/image_%d.png'
        input_idx_pattern = exp_dir_pattern % t + '/input_idx_%d.npy'
        try:
            while ambiguity > ambiguity_threshold and j < jump_limit:
                image_path = image_pattern % j
                idx_path = input_idx_pattern % j
                while not os.path.exists(image_path) or not os.path.exists(idx_path):
                    time.sleep(0.1)
                time.sleep(0.1)

                idx = np.load(idx_path)

                result = nipple.classify(image_path, rot, assumed_class, ambiguity_threshold, next_random=False,
                                         first_i=idx)
                print(tabs, result[0], result[1][1] if result[1] is not None else -1)
                if initial_class is None:
                    initial_class = result[0][4]
                if result[1] is not None:
                    (expected_ambiguity, next_rot), next_i, best_poses = result[1]
                    print(tabs, expected_ambiguity)
                    tabs += '\t'
                    all_best_poses.append((idx, best_poses))
                    j += 1
                else:
                    ambiguity = 0
                    final_class = result[0][4]
                if j == jump_limit:
                    final_class = result[0][4]
        except:
            pass
