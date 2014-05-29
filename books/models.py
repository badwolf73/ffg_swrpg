from django.db import models
import os

# Create your models here.

class System(models.Model):
  name = models.CharField(max_length=100)
  initials = models.CharField(max_length=10)
  def __unicode__(self):
    return self.name
  
class Book(models.Model):
  name = models.CharField(max_length=100)
  initials = models.CharField(max_length=10)
  num_pages = models.IntegerField()
  system = models.ForeignKey(System)
  product_key = models.CharField(max_length=10)
  def __unicode__(self):
    return "{0} ({1})".format(self.name, self.system.initials)
    
  def _item_set(self):
    return Item.objects.filter(pk__in=[x.item.id for x in self.index_set.filter(item__category__model=1)])
  def _weapon_set(self):
    return Weapon.objects.filter(pk__in=[x.item.id for x in self.index_set.filter(item__category__model=2)])
  def _armor_set(self):
    return Armor.objects.filter(pk__in=[x.item.id for x in self.index_set.filter(item__category__model=3)])
  def _attachment_set(self):
    return Attachment.objects.filter(pk__in=[x.item.id for x in self.index_set.filter(item__category__model=4)])
    
  item_set = property(_item_set)
  weapon_set = property(_weapon_set)
  armor_set = property(_armor_set)
  attachment_set = property(_attachment_set)
  
class Category(models.Model):
  MODEL_CHOICES = (
    (1, 'Item'),
    (2, 'Weapon'),
    (3, 'Armor'),
    (4, 'Attachment'),
  )
  model = models.IntegerField(choices=MODEL_CHOICES)
  name = models.CharField(max_length=50)

  def _weapon_set(self):
    if self.model == 2:
      return Weapon.objects.filter(item_ptr_id__in=[x.id for x in self.item_set.all()])
  
  weapon_set = property(_weapon_set)

  def _attachment_set(self):
    if self.model == 4:
      return Attachment.objects.filter(item_ptr_id__in=[x.id for x in self.item_set.all()])
  
  attachment_set = property(_attachment_set)

  def __unicode__(self):
    return self.name

class Skill(models.Model):
  SKILL_CHOICES = (
    (1, 'Weapon'),
  )
  skill = models.IntegerField(choices=SKILL_CHOICES)
  name = models.CharField(max_length=50)

  def __unicode__(self):
    return self.name

class RangeBand(models.Model):
  RANGE_BAND_CHOICES = (
    (1, 'Weapon'),
  )
  range_band = models.IntegerField(choices=RANGE_BAND_CHOICES)
  name = models.CharField(max_length=50)

  def __unicode__(self):
    return self.name

def get_item_image_path(instance, filename):
  if hasattr(instance, 'weapon'):
    path_start = 'weapon'
  else:
    path_start = 'item'
  return os.path.join(path_start, str(instance.id), filename)

class Item(models.Model):
  name = models.CharField(max_length=100)
  price = models.IntegerField()
  restricted = models.BooleanField()
  encumbrance = models.IntegerField()
  rarity = models.IntegerField()
  category = models.ForeignKey(Category)
  image = models.ImageField(upload_to=get_item_image_path, null=True, blank=True)
  
  def __unicode__(self):
    return self.name
    
  def _indexes(self):
    return ", ".join([idx.str() for idx in self.index_set.all()])
    
  def _display_price(self):
    if self.restricted:
      res = "(R) "
    else:
      res = ""
    if self.price:
      rprice = self.price
    else:
      rprice = "-"
    return '{0}{1}'.format(res, rprice)

  def _display_encum(self):
    if self.price or self.encumbrance:
      return str(self.encumbrance)
    else:
      return "-"

  def _display_rarity(self):
    if self.price or self.rarity:
      return str(self.rarity)
    else:
      return "-"
    
  display_price = property(_display_price)
  display_encum = property(_display_encum)
  display_rarity = property(_display_rarity)
  indexes = property(_indexes)
  
  class Meta:
    ordering = ['name']

class Index(models.Model):
  book = models.ForeignKey(Book)
  page = models.IntegerField()
  item = models.ForeignKey(Item)
  
  def __unicode__(self):
    return "{0}-{1}:{2}".format(self.book.system.initials, self.book.initials, self.page)
    
  def str(self):
    return "{0}-{1}:{2}".format(self.book.system.initials, self.book.initials, self.page)
  
class Weapon(Item):
  skill = models.ForeignKey(Skill)
  damage = models.IntegerField()
  critical = models.IntegerField()
  range_band = models.ForeignKey(RangeBand)
  hard_points = models.IntegerField()
  special = models.CharField(max_length=200)
  
  def _display_damage(self):
    if (self.skill.name in ['Melee', 'Brawl']):
      return "{0:+d}".format(self.damage)
    else:
      return self.damage
  
  def _display_crit(self):
    if self.critical:
      return str(self.critical)
    else:
      return "-"

  def _display_hp(self):
    if self.price or self.hard_points:
      return str(self.hard_points)
    else:
      return "-"
      
  display_crit = property(_display_crit)
  display_hp = property(_display_hp)
  display_damage = property(_display_damage)
  
  class Meta:
    ordering = ['name']
    
class Armor(Item):
  defense = models.IntegerField()
  soak = models.IntegerField()
  hard_points = models.IntegerField()

  def _display_hp(self):
    if self.price or self.hard_points:
      return str(self.hard_points)
    else:
      return "-"
      
  display_hp = property(_display_hp)

  class Meta:
    ordering = ['name']
    
class Attachment(Item):
  by_silhoutte = models.BooleanField()
  hard_points = models.IntegerField()
  
  def _display_price(self):
    item_price = super(Attachment, self)._display_price()
    if self.by_silhoutte:
      return "{0} x silhoutte".format(item_price)
    else:
      return item_price
      
  def _display_encum(self):
    if self.price and self.encumbrance:
      return "{0:+d}".format(self.encumbrance)
    else:
      return "-"

  display_price = property(_display_price)
  display_encum = property(_display_encum)
