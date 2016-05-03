import copy
import sys
import re

class Node(object):
    next_state_mm = 0
    next_state_ab = 0
    def __init__(self,node_name,node_depth,node_player,node_vacancies,node_score_val,node_parentname,node_board,game_cutoff,grid_values):
        self.node_name = node_name
        self.node_depth = node_depth
        self.node_player = node_player
        self.node_vacancies = node_vacancies
        self.node_score_val = node_score_val
        self.opponent_val = self.opponent(self.node_player)
        self.node_parentname = node_parentname
        self.children = []
        self.node_board = node_board
        self.game_cutoff = game_cutoff
        self.grid_values = grid_values

        if node_depth < self.game_cutoff:
            #print self.labelling(int(self.node_name)),self.node_depth,self.node_player,self.node_score_val,self.labelling(int(self.node_parentname))
            #print 'Children creation invoked'
            self.createchildren()
            #print 'Ignore below english sentence.'
        #print 'Child creation Did not happen for other instance. so repeat print'
        #print self.labelling(int(self.node_name)),self.node_depth,self.node_player,self.node_score_val,self.labelling(int(self.node_parentname))

    def labelling(self,index_num):
        labels = ['A','B','C','D','E']
        ind_to_lab = []
        if index_num >= 0:
            for i in range(0,5):
                for j in range(0,5):
                    ind_to_lab.append(labels[j]+str((i+1)))
            return ind_to_lab[index_num]
        else:
            return 'root'

    def opponent(self,op_player):
        if op_player == 'X':
            return 'O'
        else:
            return 'X'

    def createchildren(self):
        for item in self.node_vacancies:
            if self.node_depth < 2:
                self.temp_board = copy.deepcopy(self.node_board)
                #self.children.append(Node(item,self.node_depth+1,self.opponent,[el for el in self.node_vacancies if el != item],self.node_score(self.opponent),self.node_name,self.update_node_board(self.temp_board,item,self.node_player),self.game_cutoff,self.grid_values))
                self.children.append(Node(item,self.node_depth+1,self.opponent_val,[el for el in self.node_vacancies if el != item],self.update_node_board(self.temp_board,item,self.node_player)[0],self.node_name,self.update_node_board(self.temp_board,item,self.node_player)[1],self.game_cutoff,self.grid_values))

    '''
    def node_score(self,ns_player):
        if ns_player == 'X':
            return -1e309
        else:
            return 1e309


    def update_node_board(self,sample_board,single_index,player):
        row_index = single_index / len(self.node_board)
        col_index = single_index % len(self.node_board)
        sample_board[row_index][col_index] = player
        return sample_board
    '''
    def update_node_board(self,sample_board,single_index,mover):
        row_index = single_index / len(self.node_board)
        col_index = single_index % len(self.node_board)
        up,down,left,right = self.adjacency_check(row_index,col_index,sample_board)
        if up == mover or left == mover or right == mover or down == mover:
            #print "Raid update entered"
            updated_boardlist_raid = self.raid(row_index,col_index,sample_board,mover)
            #eval_after_raid = self.player_score(mover,updated_boardlist_raid) - self.player_score(self.opponent(mover),updated_boardlist_raid)
            eval_after_raid = self.player_score('X',updated_boardlist_raid) - self.player_score('O',updated_boardlist_raid)
            return eval_after_raid,updated_boardlist_raid
        else:
            #print "sneak update entered"
            #print self.labelling(int(single_index)),"is going to be sneaked by",mover
            updated_boardlist_sneak = self.sneak(row_index,col_index,sample_board,mover)
            #print updated_boardlist_sneak
            #print "score of mover:", self.player_score(mover,updated_boardlist_sneak)
            #print "Score of opp:",self.player_score(self.opponent(mover),updated_boardlist_sneak)
            #eval_after_sneak = self.player_score(mover,updated_boardlist_sneak) - self.player_score(self.opponent(mover),updated_boardlist_sneak)
            eval_after_sneak = self.player_score('X',updated_boardlist_sneak) - self.player_score('O',updated_boardlist_sneak)
            #print "Eval Score after sneak:",eval_after_sneak
            return eval_after_sneak,updated_boardlist_sneak

    '''Computation start'''

    def adjacency_check(self,row_index,col_index,boardlist):
        if row_index-1 < 0:
            up = '*'
        else:
            up = boardlist[row_index-1][col_index]
        if row_index+1 > len(boardlist)-1:
            down = '*'
        else:
            down = boardlist[row_index+1][col_index]
        if col_index-1 < 0:
            left = '*'
        else:
            left = boardlist[row_index][col_index-1]
        if col_index+1 > len(boardlist)-1:
            right = '*'
        else:
            right = boardlist[row_index][col_index+1]
        return up,down,left,right

    def raid(self, row_index, col_index,boardlist,mover):
        boardlist[row_index][col_index] = mover
        up, down, left, right = self.adjacency_check(row_index,col_index,boardlist)
        if up == self.opponent(mover):
            boardlist[row_index-1][col_index] = mover
        if left == self.opponent(mover):
            boardlist[row_index][col_index-1] = mover
        if down == self.opponent(mover):
            boardlist[row_index+1][col_index] = mover
        if right == self.opponent(mover):
            boardlist[row_index][col_index+1] = mover
        return boardlist

    def sneak(self,row_index,col_index,boardlist,mover):
        boardlist[row_index][col_index] = mover
        return boardlist

    def player_score(self,mover,boardlist):
        pscore = 0
        for i in range(len(boardlist)):
            for j in range(len(boardlist)):
                if boardlist[i][j] == mover:
                    pscore += int(self.grid_values[i][j])
        return pscore

    '''*********GBFS**********'''

    def gbfs(self,possible_moves_list,sample_board_main,mover):
        #print "GBFS Function Invoked"
        gbfs_list = []
        for single_index in possible_moves_list:
            sample_board = copy.deepcopy(sample_board_main)
            row_index = single_index / len(self.node_board)
            col_index = single_index % len(self.node_board)
            up,down,left,right = self.adjacency_check(row_index,col_index,sample_board)
            if up == mover or left == mover or right == mover or down == mover:
                updated_boardlist_raid = self.raid(row_index,col_index,sample_board,mover)
                eval_after_raid = self.player_score('X',updated_boardlist_raid) - self.player_score('O',updated_boardlist_raid)
                gbfs_list.append([row_index,col_index,eval_after_raid,'raid'])
            else:
                updated_boardlist_sneak = self.sneak(row_index,col_index,sample_board,mover)
                eval_after_sneak = self.player_score('X',updated_boardlist_sneak) - self.player_score('O',updated_boardlist_sneak)
                gbfs_list.append([row_index,col_index,eval_after_sneak,'sneak'])
        return gbfs_list

    def gbfs_next_best_move(self,gbfs_list,sample_board,mover):
        lowest_eval = -1e309
        for i in range(len(gbfs_list)):
            if lowest_eval < gbfs_list[i][2]:
                lowest_eval = gbfs_list[i][2]
                row_index = gbfs_list[i][0]
                col_index = gbfs_list[i][1]
                act = gbfs_list[i][3]
        #print lowest_eval
        #print "row is",row_index
        #print "col is",col_index
        #print "action is",act
        if act == 'sneak':
            updated_boardlist_sneak = self.sneak(row_index,col_index,sample_board,mover)
            return updated_boardlist_sneak
        else:
            updated_boardlist_raid = self.raid(row_index,col_index,sample_board,mover)
            return updated_boardlist_raid

    '''********Minimax************'''
    def minimax(self,node,depth,player):
        word = 'inf'
        rword = 'Infinity'
        if int(self.game_cutoff) == depth:
            #print "Depth Reached. So Return Value now"
            return node.node_score_val

        if player == 'X':
            #print 'X player started'
            bestvalue = -1e309
            #print self.labelling(int(node.node_name)),',',node.node_depth,',',bestvalue
            line1 = "{0},{1},{2}".format(self.labelling(int(node.node_name)),node.node_depth,bestvalue)
            line1 = re.sub(r'\b{0}\b'.format(re.escape(str(word))), rword, line1)
            print line1
            for child in node.children:
                val = self.minimax(child,child.node_depth,node.opponent_val) ## A1,1,O
                if self.game_cutoff == '1':
                    #print self.labelling(int(child.node_name)),',',child.node_depth,',',val
                    line2 = "{0},{1},{2}".format(self.labelling(int(child.node_name)),child.node_depth,val)
                    line2 = re.sub(r'\b{0}\b'.format(re.escape(str(word))), rword, line2)
                    print line2
                if val > bestvalue:
                    bestvalue = max(bestvalue,val)
                    self.next_state_mm = child.node_name
                #print self.labelling(int(child.node_parentname)),',',child.node_depth-1,',',bestvalue
                line3 = "{0},{1},{2}".format(self.labelling(int(child.node_parentname)),child.node_depth-1,bestvalue)
                line3 = re.sub(r'\b{0}\b'.format(re.escape(str(word))), rword, line3)
                print line3
            return bestvalue

        elif player == 'O':
            #print 'O player started'
            bestvalue = 1e309
            #print self.labelling(int(node.node_name)),',',node.node_depth,',',bestvalue
            line4 = "{0},{1},{2}".format(self.labelling(int(node.node_name)),node.node_depth,bestvalue)
            line4 = re.sub(r'\b{0}\b'.format(re.escape(str(word))), rword, line4)
            print line4
            for child in node.children:
                #print self.labelling(int(child.node_name)),',',child.node_depth,',',child.node_score_val
                line5 = "{0},{1},{2}".format(self.labelling(int(child.node_name)),child.node_depth,child.node_score_val)
                line5 = re.sub(r'\b{0}\b'.format(re.escape(str(word))), rword, line5)
                print line5
                val = self.minimax(child,child.node_depth,child.node_name)
                bestvalue = min(bestvalue,val)
                #print self.labelling(int(child.node_parentname)),',',child.node_depth-1,',',bestvalue
                line6 = "{0},{1},{2}".format(self.labelling(int(child.node_parentname)),child.node_depth-1,bestvalue)
                line6 = re.sub(r'\b{0}\b'.format(re.escape(str(word))), rword, line6)
                print line6
            return bestvalue

    '''******Alpha-Beta Pruning*********'''
    def alphabeta(self,node,depth,alpha,beta,player):
        word = 'inf'
        rword = 'Infinity'
        if int(self.game_cutoff) == depth:
            return node.node_score_val

        if player == 'X':
            bestvalue = -1e309
            #print self.labelling(int(node.node_name)),',',node.node_depth,',',bestvalue,',',alpha,',',beta
            line1 = "{0},{1},{2},{3},{4}".format(self.labelling(int(node.node_name)),node.node_depth,bestvalue,alpha,beta)
            line1 = re.sub(r'\b{0}\b'.format(re.escape(str(word))), rword, line1)
            print line1
            for child in node.children:
                bestvalue = max(bestvalue,self.alphabeta(child,child.node_depth,alpha,beta,node.opponent_val))
                if bestvalue > alpha:
                    self.next_state_ab = child.node_name
                    alpha = max(alpha,bestvalue)
                line2 = "{0},{1},{2},{3},{4}".format(self.labelling(int(child.node_parentname)),child.node_depth-1,bestvalue,alpha,beta)
                line2 = re.sub(r'\b{0}\b'.format(re.escape(str(word))), rword, line2)
                print line2
                #print self.labelling(int(child.node_parentname)),',',child.node_depth-1,',',bestvalue,',',alpha,',',beta
                if beta <= alpha:
                    break
            return bestvalue

        elif player == 'O':
            bestvalue = 1e309
            #print self.labelling(int(node.node_name)),',',node.node_depth,',',bestvalue,',',alpha,',',beta
            line3 = "{0},{1},{2},{3},{4}".format(self.labelling(int(node.node_name)),node.node_depth,bestvalue,alpha,beta)
            line3 = re.sub(r'\b{0}\b'.format(re.escape(str(word))), rword, line3)
            print line3
            for child in node.children:
                #print self.labelling(int(child.node_name)),',',child.node_depth,',',child.node_score_val,',',alpha,',',beta
                line4 = "{0},{1},{2},{3},{4}".format(self.labelling(int(child.node_name)),child.node_depth,child.node_score_val,alpha,beta)
                line4 = re.sub(r'\b{0}\b'.format(re.escape(str(word))), rword, line4)
                print line4
                bestvalue = min(bestvalue,self.alphabeta(child,child.node_depth,alpha,beta,child.node_name))
                #print self.labelling(int(child.node_parentname)),child.node_depth-1,bestvalue,alpha,beta
                beta = min(beta,bestvalue)
                #print self.labelling(int(child.node_parentname)),',',child.node_depth-1,',',bestvalue,',',alpha,',',beta
                line5 = "{0},{1},{2},{3},{4}".format(self.labelling(int(child.node_parentname)),child.node_depth-1,bestvalue,alpha,beta)
                line5 = re.sub(r'\b{0}\b'.format(re.escape(str(word))), rword, line5)
                print line5
                if beta <= alpha:
                    break
            return bestvalue


    def print_next_state(self,single_index,sample_board,mover):
        row_index = single_index / len(self.node_board)
        col_index = single_index % len(self.node_board)
        up,down,left,right = self.adjacency_check(row_index,col_index,sample_board)
        if up == mover or left == mover or right == mover or down == mover:
            updated_boardlist_raid = self.raid(row_index,col_index,sample_board,mover)
            return updated_boardlist_raid
        else:
            updated_boardlist_sneak = self.sneak(row_index,col_index,sample_board,mover)
            return updated_boardlist_sneak

    def display(self,sample_board):
        for i in range(0,5):
            for j in range(0,5):
                #grid_positions[i][j],
                sys.stdout.write(sample_board[i][j])
                #return grid_positions
            print

def main():

    f1 = open("input.txt","r")
    #f1 = open(sys.argv[2],"r")
    if f1.mode == 'r':
        fl = f1.read().splitlines()

    task = fl[0]
    player = fl[1]
    cutoffdepth = fl[2]
    grid_values = []
    grid_positions = []
    spotslist = []

    for i in range(3,8):
        grid_values.append(fl[i].split())
    #print grid_values
    #print grid values in list format

    for i in range(8,13):
        grid_positions.append(list(fl[i]))
    #print grid_positions
    #prints grid positions in list format

    def spots(arrtolist):
        for i in range(len(arrtolist)):
            for j in range(len(arrtolist)):
                if arrtolist[i][j] == '*':
                     spotslist.append(i*5+j)
        return spotslist
    #creates a list of available moves at start of game
    #print spots(grid_positions)

    n = Node(-1,0,player,spots(grid_positions),-1e309,-1,grid_positions,cutoffdepth,grid_values)
    #Nodename: -1 for root, Initial depth = 0, Initial Value is -infinity for X, Parent is root itself

    if task == '1':
        print "Greedy Best First Search Algorithm created file"
        #f0 = open("GBFS next_state.txt","w+")
        f0 = open("next_state.txt","w+")
        sys.stdout = f0
        gbfs_eval_list = n.gbfs(spots(grid_positions),grid_positions,player)
        n.display(n.gbfs_next_best_move(gbfs_eval_list,grid_positions,player))
        f0.close()
        #calls greedy-best first search

    elif task == '2':
        print "Minimax Algorithm created file"
        #f1 = open("Minimax traverse_log.txt","w+")
        f1 = open("traverse_log.txt","w+")
        sys.stdout = f1
        print 'Node,Depth,Value'
        n.minimax(n,0,player)
        #print "Next state of minimax is:",n.labelling(int(n.next_state_mm))
        f1.close()
        #f2 = open("Minimax next_state.txt","w+")
        f2 = open("next_state.txt","w+")
        sys.stdout = f2
        n.display(n.print_next_state(int(n.next_state_mm),grid_positions,player))
        f2.close()


    elif task == '3':
        print "Alpha-Beta Pruning Algorithm created file"
        #f3 = open("Alpha-Beta traverse_log.txt","w+")
        f3 = open("traverse_log.txt","w+")
        sys.stdout = f3
        print "Node,Depth,Value,Alpha,Beta"
        n.alphabeta(n,0,-1e309,1e309,player)
        #print "Next state of alpha-beta pruning is:",n.labelling(int(n.next_state_ab))
        #f2.write(n.labelling(int(n.next_state_ab)))
        f3.close()
        #f4 = open("Alpha-Beta next_state.txt","w+")
        f4 = open("next_state.txt","w+")
        sys.stdout = f4
        n.display(n.print_next_state(int(n.next_state_ab),grid_positions,player))
        f4.close()
        #calls alpha-beta pruning


    else:
        print "Invalid game-style command"


if __name__ == '__main__':
    main()