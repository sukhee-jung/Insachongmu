class KurlyCluster:
    def __init__(self, channel, nx, ny, name):
        self.channel = channel
        self.nx = nx
        self.ny = ny
        self.name = name

# 컬리 클러스터 슬랙 채널 목록
clusters = [
    KurlyCluster('C05NXMZP62Y', '56', '127', '김포 클러스터'),
]
