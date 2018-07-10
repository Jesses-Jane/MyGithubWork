import numpy as np
import matplotlib.pyplot as plt
import math
import os
import csv
import multiprocessing
import time
import shutil

class Run_PyFile(multiprocessing.Process):
    def __init__(self, filename):
        multiprocessing.Process.__init__(self)
        self.filename = filename

    def run(self):
        os.system(self.filename)
        # target = run_batFile(self.filename)
def get_databycsvfile(filename):
    if os.path.exists(filename)==False:
         return
    file_data = csv.reader(open(filename), dialect='excel')
    data = []
    for each_item in file_data:
        data.append(each_item)
    return data

def create_ansysbatfile(ansys_path,work_path,bat_file,apdl_file):
    apdl_filename = os.path.basename(apdl_file)
    flist = []
    flist.append("@echo off \n")
    flist.append(work_path.split(":")[0] + ":\n")
    flist.append("cd " + work_path + "\n")
    flist.append('"' + ansys_path + '"' + " -b -p ane3fl -np 1 -i " + apdl_filename + " -o out.txt")
    f = open(bat_file, "w+")
    f.writelines(flist)
    f.close()
def modify_fileString(filename,find_str,replace_str):
    with open(filename,'r',encoding='utf-8') as f_read:
        oldlist=[]
        for item in f_read:
            oldlist.append(item)
    with open(filename,'w',encoding='utf-8') as f_write:
        for item in oldlist:
            current_line = item
            if str(item).find(find_str)!=-1:
                current_line=find_str+replace_str+"\n"
            f_write.write(current_line)
    f_read.close()
    f_write.close()
def run_batFile(filename):
    current_path=os.path.dirname(filename)
    for file in os.listdir(current_path):
        if file.find("file.lock")!=-1 or file.find(".csv")!=-1  :
            try:
                os.remove(current_path+"\\"+file)
            except (OSError,IOError) as e:
                logging.debug(e)
                logging.warning("file(.lock or.csv) is opened by another application.")
    temp_command=os.path.sep.join(filename.split(r'/'))
    os.system(temp_command)
def modify_ansysconfigfile(work_path,a,b,r):
    ansys_path = 'C:\Program Files\ANSYS Inc\\v150\ANSYS\\bin\winx64\\ansys150.exe'
    # work_path='D:\Programming\PSO\\result'
    filename='ansys_solution'
    apdl_file=work_path+'\\'+filename+'.txt'
    bat_file =work_path+'\\'+filename+'.bat'
    csv_file =work_path+'\\'+filename+'.csv'
    create_ansysbatfile(ansys_path,work_path,bat_file,apdl_file)
    modify_fileString(apdl_file, "a=", "%s" % str(a))
    modify_fileString(apdl_file, "b=", "%s" % str(b))
    modify_fileString(apdl_file, "r=", "%s" % str(r))
    modify_fileString(apdl_file, "filename=", "'%s'" % filename)
    # run_batFile(bat_file)
    # if os.path.exists(csv_file):
    #     result_data=get_databycsvfile(csv_file)
    #     max_stress=float(result_data[0][1])
    #     return max_stress
    # else:
    #     return None
def get_ansysresult(arr_x):
    mask_number=arr_x.shape[0]
    current_path='D:\Programming\PSO'
    process_list= []
    result_list = []
    for i in range(0, mask_number):
        work_path=current_path+'\\result_%s'%str(i+1)
        bat_file =current_path+'\\result_%s'%str(i+1)+'\\ansys_solution.bat'
        modify_ansysconfigfile(work_path,arr_x[i][0],arr_x[i][1],arr_x[i][2])
        p=Run_PyFile(bat_file)
        process_list.append(p)
    for i in range(0, mask_number):
        process_list[i].start()
    for i in range(0, mask_number):
        process_list[i].join()
    for i in range(0, mask_number):
        csv_file = current_path + '\\result_%s' % str(i + 1) + '\\ansys_solution.csv'
        result_data = get_databycsvfile(csv_file)
        max_stress=float(result_data[0][1])
        result_list.append(max_stress)
    return result_list
class PSO(object):
    def __init__(self, population_size, max_steps):
        self.w = 0.4         # 惯性权重
        self.c1 = self.c2 = 2
        self.population_size = population_size  # 粒子群数量
        self.dim = 3  # 搜索空间的维度
        self.max_steps = max_steps  # 迭代次数
        self.x1_bound = [8, 12]
        self.x2_bound = [8, 12]    # 解空间范围
        self.x3_bound = [1, 3]     # 解空间范围
        self.x1 = np.random.uniform(self.x1_bound[0], self.x1_bound[1],
                                   (self.population_size, 1))  # 初始化粒子群位置
        self.x2 = np.random.uniform(self.x2_bound[0], self.x2_bound[1],
                                   (self.population_size, 1))  # 初始化粒子群位置
        self.x3 = np.random.uniform(self.x3_bound[0], self.x3_bound[1],
                                   (self.population_size, 1))

        self.x=np.hstack((self.x1,self.x2,self.x3))

        self.v = np.random.rand(self.population_size, self.dim)  # 初始化粒子群速度
        fitness = self.calculate_fitness(self.x)
        self.p = self.x  # 个体的最佳位置
        self.pg = self.x[np.argmin(fitness)]  # 全局最佳位置
        self.individual_best_fitness = fitness  # 个体的最优适应度
        self.global_best_fitness = np.min(fitness)  # 全局最佳适应度

    def calculate_fitness(self, x):
        fit = np.zeros(( x.shape[0]))
        result=get_ansysresult(x)
        for i in range(0,x.shape[0]):
            mass=(x[i][0]*x[i][1])-4*math.pi*x[i][2]
            stress=result[i]
            if (stress)>300:
                hk=mass*10000
            else:
                hk=0
            fit[i]=mass+hk
        return fit
        # return np.sum(np.square(x), axis=1)

    def evolve(self):
        fig = plt.figure()
        for step in range(self.max_steps):
            r1 = np.random.rand(self.population_size, self.dim)
            r2 = np.random.rand(self.population_size, self.dim)
            # 更新速度和权重
            self.v = self.w * self.v + self.c1 * r1 * (self.p - self.x) + self.c2 * r2 * (self.pg - self.x)
            self.x = self.v + self.x
            for bird in self.x:

                if (bird[0]<8):
                    bird[0]=8
                if (bird[0]>12):
                    bird[0]=12

                if (bird[1] < 8):
                    bird[1] = 8
                if (bird[1] > 12):
                    bird[1] = 12

                if (bird[2]<1):
                    bird[2]=1
                if (bird[2]>3):
                    bird[2]=3

            plt.clf()
            plt.scatter(self.x[:, 0], self.x[:, 1], s=30, color='k')
            plt.xlim(self.x1_bound[0], self.x1_bound[1])
            plt.ylim(self.x2_bound[0], self.x2_bound[1])
            plt.pause(0.01)
            fitness = self.calculate_fitness(self.x)
            # 需要更新的个体
            update_id = np.less(fitness,self.individual_best_fitness)
            self.p[update_id] = self.x[update_id]
            self.individual_best_fitness[update_id] = fitness[update_id]
            # 新一代出现了更小的fitness，所以更新全局最优fitness和位置
            convergence_value=np.min(fitness) -self.global_best_fitness
            if np.min(fitness) < self.global_best_fitness:
                self.pg = self.x[np.argmin(fitness)]
                self.global_best_fitness = np.min(fitness)
            print('iteration: %s，best fitness: %.5f, mean fitness: %.5f,convergence: %s' % (step+1,self.global_best_fitness, np.mean(fitness),convergence_value))
            # 收敛准则
            if abs(convergence_value)<0.01:
                break
        print(self.pg )
if __name__ == '__main__':
# freeze_support()
    pso = PSO(10, 20)
    pso.evolve()
    plt.show()

# run_ansys(10,6,2)
