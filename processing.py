import os
import subprocess

def run_command(command):
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the command: {e}")

#path to the main repository containing the patients
dataset_path = ""

#if you are using Windows, convert the dataset_path to a Linux type
docker_dataset_path = ""

#Perform Skull stripping using Synthstrip - docker image
def run_skull_stripping(dataset_path, docker_dataset_path):
    for patient in os.listdir(dataset_path):
        for timepoint in os.listdir(os.path.join(dataset_path, patient)):
            os.makedirs(os.path.join(dataset_path, patient, timepoint, 'processed'), exist_ok=True)
            for file in os.listdir(os.path.join(dataset_path, patient, timepoint, 'raw')):
                # Construct the Docker command
                if '.nii.gz' in file:
                    input_file = os.path.join(dataset_path, patient, timepoint, 'raw', file)

                    # Convert to Docker paths
                    docker_input_path = f"{docker_dataset_path}/{patient}/{timepoint}/raw"
                    docker_input_file = f"{docker_input_path}/{file}"
                    docker_output_file = f"{docker_dataset_path}/{patient}/{timepoint}/processed/brain_{file}"
                    docker_mask_file = f"{docker_dataset_path}/{patient}/{timepoint}/processed/mask_{file}"
                    
                    cmd = [
                            "docker", "run", "--rm",
                            "-v", f"{dataset_path}:{docker_dataset_path}",  # Mount dataset
                            "freesurfer/synthstrip",
                            "-i", docker_input_file,
                            "-o", docker_output_file,
                            "-m", docker_mask_file,
                    ]
                    print(f"Processing: {file} (Patient: {patient}, Timepoint: {timepoint})")
                        
                    # Run the command
                    subprocess.run(cmd, shell=True)

def run_N4Bias(path):
    for patient in os.listdir(path):
        print('N4 - ', patient)
        for timepoint in os.listdir(os.path.join(path, patient)):
            for file in os.listdir(os.path.join(path, patient, timepoint, 'processed')):
                if 'brain' in file:
                    print('N4 - ', patient, timepoint, file)
                    file_path = os.path.join(path, patient, timepoint, 'processed', file)
                    output_file = os.path.join(path, patient, timepoint, 'processed', 'n4_'+file)
                    run_command(['N4BiasFieldCorrection', "-d", "3", "-i", file_path, '-o', output_file])

run_skull_stripping(dataset_path, docker_dataset_path)
run_N4Bias(dataset_path)
